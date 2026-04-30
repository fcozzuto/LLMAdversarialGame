def choose_move(observation):
    w = int(observation.get("grid_width") or 8) or 8
    h = int(observation.get("grid_height") or 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # If no resources visible, move to keep distance from opponent while staying central-ish.
    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(nx, ny, ox, oy)
            val = -d_me + 0.15 * d_op
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Choose resource that is good for us and harder for the opponent to reach.
    best_move = (0, 0)
    best_score = -10**18

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        move_score = 0
        # Prefer immediate pickup direction when landing on resource.
        if (nx, ny) in set(resources):
            move_score += 1000

        # Evaluate best target under this move.
        local_best = -10**18
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Smaller is better for us; larger is better relative to opponent.
            # Add slight bias toward closer resources for determinism.
            val = -d_my + 0.35 * d_op - 0.01 * (abs(rx - (w // 2)) + abs(ry - (h // 2)))
            if val > local_best:
                local_best = val
        move_score += local_best

        # Avoid stepping into obvious opponent chase: reduce chance of becoming closer than necessary.
        move_score -= 0.08 * cheb(nx, ny, ox, oy)

        if move_score > best_score:
            best_score = move_score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]