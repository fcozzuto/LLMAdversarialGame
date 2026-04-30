def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose target resource: nearest to us, tie-break by farthest from opponent
    if resources:
        best = None
        for rx, ry in resources:
            d_us = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            cand = (d_us, -d_op, rx, ry)
            if best is None or cand < best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (10**9, 10**9, 10**9, 0, 0)  # (score, -oppDist, nx, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_new = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Score: prioritize reducing distance to target, then increase opponent distance
        # Deterministic tie-break by coordinates
        score = (d_new, -d_opp, nx, ny)
        if score < best_move[:4]:
            best_move = (score[0], score[1], score[2], dx, dy)

    return [int(best_move[3]), int(best_move[4])]