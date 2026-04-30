def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    best_move = None
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Prefer resources we can reach no later than the opponent.
        # Value is (our_dist - opp_dist) averaged by best target (min).
        val = None
        for rx, ry in resources:
            v = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
            if val is None or v < val:
                val = v
        # Small tie-breakers: don't be stationary unless no better alternative
        v2 = val
        if (dx, dy) == (0, 0):
            v2 += 0.01
        # Prefer moves that reduce distance to the currently most favorable target
        # by also minimizing our best distance.
        best_my = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if best_my is None or myd < best_my:
                best_my = myd
        v2 += best_my * 0.001
        if best_val is None or v2 < best_val or (v2 == best_val and (dx, dy) < best_move):
            best_val = v2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]