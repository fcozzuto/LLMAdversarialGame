def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    def best_target():
        best = None
        best_score = -10**18
        for rx, ry in resources:
            dself = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer resources where we are earlier than opponent; tie-break by nearer to us.
            score = (dop - dself) * 100 - dself
            if score > best_score or (score == best_score and (rx, ry) < (best[0], best[1])):
                best_score = score
                best = (rx, ry)
        return best

    if resources:
        target = best_target()
    else:
        target = (w // 2, h // 2)

    tx, ty = int(target[0]), int(target[1])

    # Move that reduces distance to target most, with deterministic tie-break; also avoid stepping into blocked.
    best_move = (0, 0)
    best_dist = 10**9
    best_adv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Secondary: prefer moves where opponent is not getting closer to our chosen target than us.
        adv = (cheb(ox, oy, tx, ty) - d)
        if d < best_dist or (d == best_dist and (adv > best_adv or (adv == best_adv and (dx, dy) < best_move))):
            best_dist = d
            best_adv = adv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]