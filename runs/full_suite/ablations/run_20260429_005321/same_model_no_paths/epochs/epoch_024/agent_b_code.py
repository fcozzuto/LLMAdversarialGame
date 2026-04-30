def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if (sx, sy) in set((r[0], r[1]) for r in resources if len(r) >= 2):
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None  # (score, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, cx, cy)
        if not resources:
            score = -myd
        else:
            dmin = 10**9
            doppmin = 10**9
            for r in resources:
                if len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                d = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                if d < dmin:
                    dmin, doppmin = d, d2
            score = (doppmin - dmin) * 10 - myd
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]