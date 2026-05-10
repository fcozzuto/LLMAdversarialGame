def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    self_terr = set((int(p[0]), int(p[1])) for p in observation.get("self_territory", []) or [])
    opp_terr = set((int(p[0]), int(p[1])) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set((int(p[0]), int(p[1])) for p in observation.get("unclaimed_cells", []) or [])
    obstacles = set((int(p[0]), int(p[1])) for p in observation.get("obstacles", []) or [])

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr) if opp_terr else [(ox, oy)]

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    def adj_counts(x, y):
        ua = 0
        oa = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                ua += 1
            if (nx, ny) in opp_terr:
                oa += 1
        return ua, oa

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ua, oa = adj_counts(nx, ny)
        d = min_dist_to_opp(nx, ny)

        if (nx, ny) in self_terr:
            base = 1.0 + 0.4 * ua - 0.2 * oa
        elif (nx, ny) in opp_terr:
            base = 8.0 + 1.2 * ua - 0.6 * oa
        elif (nx, ny) in unclaimed:
            base = 4.0 + 0.8 * ua - 0.4 * oa
        else:
            base = 2.0 + 0.2 * ua - 0.3 * oa

        exposure_penalty = 0.25 * oa
        opp_proximity_penalty = 0.15 * (8 - min(8, d))  # closer to opponent territory is worse
        val = base - exposure_penalty - opp_proximity_penalty

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best