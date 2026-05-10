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

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def min_dist_to_opp(x, y):
        best = abs(ox - x) + abs(oy - y)
        for px, py in opp_terr:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    opp_cent = None
    if opp_terr:
        sx0 = sum(p[0] for p in opp_terr)
        sy0 = sum(p[1] for p in opp_terr)
        opp_cent = (sx0 // len(opp_terr), sy0 // len(opp_terr))
    else:
        opp_cent = (ox, oy)

    best = None
    best_sc = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_terr:
            sc += 8
        if (nx, ny) in unclaimed:
            sc += 4
        if (nx, ny) in self_terr:
            sc += 1

        self_adj = 0
        opp_adj = 0
        for ddx, ddy in dirs4:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in self_terr:
                self_adj += 1
            if (ax, ay) in opp_terr:
                opp_adj += 1
        sc += 0.8 * self_adj
        sc -= 0.9 * opp_adj

        dxopp = abs(opp_cent[0] - nx) + abs(opp_cent[1] - ny)
        sc -= 0.15 * dxopp

        key = (sc, -dx, -dy)
        if sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]