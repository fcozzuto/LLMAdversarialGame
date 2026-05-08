def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        x, y = r[0], r[1]
        if inb(x, y) and (x, y) not in obs:
            self_d = abs(x - sx) + abs(y - sy)
            opp_d = abs(x - ox) + abs(y - oy)
            res.append((x, y, self_d, opp_d))
    if not res:
        return [0, 0]

    # Prefer moves that improve our worst-case standing across the top contested resources.
    # This is a min-max over likely races rather than chasing only one target.
    res.sort(key=lambda t: (t[3] - t[2], -t[2]), reverse=True)
    topk = res[:6] if len(res) > 6 else res

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        worst_adv = 10**18
        best_our = 10**18
        for x, y, self_d0, opp_d0 in topk:
            self_d = md(nx, ny, x, y)
            opp_d = opp_d0
            adv = opp_d - self_d
            if adv < worst_adv:
                worst_adv = adv
            if self_d < best_our:
                best_our = self_d
        # Also mildly discourage getting stuck near obstacles by preferring moves that have a
        # lower total distance to the best few resources (tie-break).
        val = worst_adv * 1000 - best_our
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]