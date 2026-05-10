def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        flip = 1.0 if (nx, ny) in opp_terr else 0.0
        claim = 1.0 if (nx, ny) in unclaimed else (0.2 if (nx, ny) in self_terr else 0.0)
        a_self = adj_count(nx, ny, self_terr)
        a_opp = adj_count(nx, ny, opp_terr)
        d_opp = min_dist_to_opp(nx, ny)

        # Prefer: direct flips/claims, then closeness to opponent, while not walking into opponent adjacency.
        val = 12.0 * flip + 6.0 * claim + 2.2 * a_self - 2.5 * a_opp - 0.12 * d_opp
        # Deterministic tie-break: stable ordering by dx,dy already in dirs8
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best