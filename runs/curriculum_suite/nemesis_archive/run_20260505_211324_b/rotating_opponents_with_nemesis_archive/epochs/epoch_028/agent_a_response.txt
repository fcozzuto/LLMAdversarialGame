def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (None, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        s_pos = (nx, ny)

        # Score a move by predicted advantage over the opponent for the best contestable resource
        # (larger is better). Include slight center bias to avoid dithering.
        cur_best_adv = -10**9
        min_self = 10**9
        for rx, ry in res:
            sr = md(s_pos, (rx, ry))
            orr = md((ox, oy), (rx, ry))
            # Advantage: how much closer we are than opponent (or how much we prevent them)
            adv = (orr - sr) * 10 - sr
            # Prefer grabbing resources that are relatively close for us
            adv -= 2 * (sr == 0)
            if sr < min_self:
                min_self = sr
            if adv > cur_best_adv:
                cur_best_adv = adv

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -0.1 * (abs(nx - cx) + abs(ny - cy))
        val = cur_best_adv + center_bias
        # Tie-break deterministically toward decreasing distance to the nearest resource
        if val > best[1] or (val == best[1] and (min_self < best[0][0])):
            best = ((min_self, dx, dy), val)

    return [best[0][1], best[0][2]]