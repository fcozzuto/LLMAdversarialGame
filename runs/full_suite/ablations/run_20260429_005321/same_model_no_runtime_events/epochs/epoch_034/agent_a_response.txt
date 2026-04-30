def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Target resources where we are relatively closer than the opponent (deterministic race with tie-break)
        best = None
        bestk = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            k = (od - sd, -sd, -cheb(ox, oy, (sx + rx) // 2, (sy + ry) // 2))
            if bestk is None or k > bestk:
                bestk = k
                best = (rx, ry)
        tx, ty = best

    # Move greedily toward target but prefer moves that keep opponent farther from target than we are
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        selfd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # oppd constant per target, but we use relative distance to discourage stepping into opponent's favorable route
        rel = (oppd - selfd)
        # Also discourage staying if there is a strictly better approach move
        k = (rel, -selfd, -abs((nx - ox)) - abs((ny - oy)), 0 if (dx == 0 and dy == 0) else 1)
        if best_score is None or k > best_score:
            best_score = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]