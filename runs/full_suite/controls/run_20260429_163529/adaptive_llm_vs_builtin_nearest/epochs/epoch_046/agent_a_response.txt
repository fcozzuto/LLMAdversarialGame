def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obs:
                    res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not res:
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = (-10**18, 0, 0)
        cur_do = cheb(sx, sy, ox, oy)
        for i, (dx, dy) in enumerate(dirs):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            nd = cheb(nx, ny, ox, oy)
            val = (nd - cur_do) - 0.01 * i
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # target: nearest resource in Chebyshev metric (diagonals)
    tx, ty = min(res, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_dr = cheb(sx, sy, tx, ty)
    cur_do = cheb(sx, sy, ox, oy)
    best_val = -10**18
    best_move = (0, 0)

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        nd_r = cheb(nx, ny, tx, ty)
        nd_o = cheb(nx, ny, ox, oy)

        # primary: make progress toward target resource
        progress = cur_dr - nd_r

        # secondary: avoid getting too close to opponent; prefer increasing distance or keeping it safe
        safe_dist = 2
        opp_pen = 0
        if nd_o <= safe_dist:
            opp_pen = (safe_dist - nd_o + 1) * 3
        # if opponent can "shadow" (move closer than we do), discourage
        opp_trend = (cur_do - nd_o)
        # lower opp_trend is better (we want distance not to shrink)
        opp_trend_pen = max(0, opp_trend) * 1.5

        # tertiary: mild preference for staying aligned toward target (ties)
        align = abs((nx - tx)) + abs((ny - ty))
        val = progress * 5.0 - opp_pen - opp_trend_pen - 0.01 * align - 1e-6 * i

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]