def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    def adj4(x, y, S):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in S:
                c += 1
        return c

    def nearest_unclaimed_dist(x, y):
        if not unclaimed:
            return 10**9
        best = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0.0

        in_self = (nx, ny) in self_terr
        in_opp = (nx, ny) in opp_terr
        in_un = (nx, ny) in unclaimed

        if in_un:
            sc += 6.0
        elif in_opp:
            sc += 2.5
        if in_self:
            sc += 1.5

        # Encourage expansion along our boundary, discourage stepping into opponent clusters.
        sc += 1.2 * adj4(nx, ny, self_terr)
        sc += 0.4 * adj4(nx, ny, unclaimed)
        opp_adj = adj4(nx, ny, opp_terr)
        sc -= 2.8 * opp_adj

        d_opp = min_dist_to_opp(nx, ny)
        if d_opp <= 1:
            sc -= 8.0
        elif d_opp <= 2:
            sc -= 3.0
        else:
            sc += 0.25 * d_opp

        # Prefer moves that reduce distance to some unclaimed cell.
        sc += 1.1 * max(0, 6 - nearest_unclaimed_dist(nx, ny)) * 0.2

        # Deterministic tie-break: closer to target direction toward center-ish unclaimed/opp balance.
        tie = 0
        tie += (nx - sx) * 0 + (ny - sy) * 0
        if in_un:
            tie = abs(nx - w // 2) + abs(ny - h // 2)
        else:
            tie = min(abs(nx - p[0]) + abs(ny - p[1]) for p in opp_list) if opp_list else 0
        sc -= 0.001 * tie

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return [int(best[0]), int(best[1])]