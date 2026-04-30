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
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        bx = (w - 1) - ox
        by = (h - 1) - oy
        best = (10**9, -10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v1 = cheb(nx, ny, bx, by)
            v2 = cheb(nx, ny, ox, oy)
            cand = (v1, -v2, -dx, -dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    best = (10**18, -10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = 10**9
        op_d = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < my_d: my_d = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < op_d: op_d = d2
        # Prefer decreasing our nearest-resource distance; also prefer staying away if opponent is closer.
        score1 = my_d * 100 + (1 if op_d < my_d else 0) * 15 + (cheb(nx, ny, ox, oy) < 2) * 7
        score2 = cheb(nx, ny, ox, oy)  # larger is better
        cand = (score1, -score2, -dx, -dy)
        if cand < best:
            best = cand
    return [best[2], best[3]]