def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    def best_resource_value(px, py):
        bestv = 10**18
        bestm = 10**18
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            v = myd - int(od * 9 // 10)  # prefer being closer than opponent
            if v < bestv or (v == bestv and myd < bestm):
                bestv = v
                bestm = myd
        return bestv, bestm

    best_move = (0, 0)
    best_tuple = (10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v, myd = best_resource_value(nx, ny)
        # tie-break: avoid stepping closer to opponent if values equal
        od = cheb(nx, ny, ox, oy)
        cand = (v, od if v == best_tuple[0] else myd)
        if cand[0] < best_tuple[0] or (cand[0] == best_tuple[0] and cand[1] < best_tuple[1]):
            best_tuple = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]