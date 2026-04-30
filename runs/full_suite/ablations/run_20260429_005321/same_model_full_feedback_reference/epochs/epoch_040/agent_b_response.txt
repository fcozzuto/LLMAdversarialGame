def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        target = ((w - 1) // 2, (h - 1) // 2)
    else:
        best_t = resources[0]
        best_adv = -10**18
        # Choose resource where we are relatively closer than opponent (deterministic).
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = (od - sd) * 1000 - sd  # prioritize winning a contest, then speed
            if adv > best_adv:
                best_adv = adv
                best_t = (rx, ry)
        target = best_t

    tx, ty = target
    # If contest is unfavorable, drift toward a safer diagonal funnel: maximize distance from opponent while still approaching.
    prefer_far = (not resources) or (cheb(sx, sy, tx, ty) >= cheb(ox, oy, tx, ty))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target. Secondary: avoid opponent when losing contest.
        val = -nd * 1000
        if prefer_far:
            val += od
        else:
            # try to reduce opponent distance to target less; lightly discourage moving toward opponent
            val += (od * 0.05)
        # Tiebreak: deterministic preference order encoded by moves list (earlier wins).
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]