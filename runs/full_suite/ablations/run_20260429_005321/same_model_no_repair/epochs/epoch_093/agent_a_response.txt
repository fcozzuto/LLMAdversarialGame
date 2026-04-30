def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh_obst = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        p = 0
        for dx, dy in neigh_obst:
            if (x + dx, y + dy) in obst:
                p += 1
        return p

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = 10**9
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, cx, cy) + 0.25 * obst_pen(nx, ny)
            if v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    res = resources[:]
    def res_key(p):
        return cheb(sx, sy, p[0], p[1]), p[0], p[1]
    res.sort(key=res_key)
    targets = res[: min(4, len(res))]

    best = None
    bestv = 10**9
    for dx, dy, nx, ny in legal:
        myd_best = 10**9
        v = 0.0
        for tx, ty in targets:
            myd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer getting closer than opponent to some target; keep it deterministic.
            v += myd * 1.0 + 0.55 * (od - myd)
            if myd < myd_best:
                myd_best = myd
        v += 0.35 * obst_pen(nx, ny)
        v += 0.02 * cheb(nx, ny, sx, sy)  # mild preference for small moves
        if v < bestv - 1e-12:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]