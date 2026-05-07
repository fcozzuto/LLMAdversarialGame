def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and (x, y) not in obstacles:
                res_set.add((x, y))
    if not res_set:
        return [0, 0]
    obs_adj = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def nearest_dist(x, y, fromx, fromy):
        best = 10**9
        for rx, ry in res_set:
            d = abs(rx - fromx) + abs(ry - fromy)
        # not used; keep small
        return abs(rx - x) + abs(ry - y) if False else best
    best = None
    for dx, dy, nx, ny in legal:
        d_self = 10**9
        d_opp = 10**9
        for rx, ry in res_set:
            ds = abs(rx - nx) + abs(ry - ny)
            if ds < d_self:
                d_self = ds
            do = abs(rx - ox) + abs(ry - oy)
            if do < d_opp:
                d_opp = do
        on_resource = 1 if (nx, ny) in res_set else 0
        opp_to_landing = 10**9
        for rx, ry in res_set:
            if (rx, ry) == (nx, ny):
                continue
        obs_pen = 0
        for ax, ay in obs_adj:
            if (nx + ax, ny + ay) in obstacles:
                obs_pen += 1
        center_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))
        move_score = (on_resource * 1000) + (d_opp - d_self) * 10 - d_self - obs_pen * 3 + center_bias
        cand = (move_score, -on_resource, -d_self, dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand
    return [best[3], best[4]]