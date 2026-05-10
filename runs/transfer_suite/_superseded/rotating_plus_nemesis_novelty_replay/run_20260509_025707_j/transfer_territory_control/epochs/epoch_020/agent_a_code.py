def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Small deterministic tie-break: fixed move order already.
    dir_priority = neigh8

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(cellset, x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in cellset:
                c += 1
        return c

    # If opponent is ahead, bias defense (avoid entering opponent territory unless it helps intercept).
    myc = observation.get("self_territory_count", len(self_cells))
    oppc = observation.get("opponent_territory_count", len(opp_cells))
    opp_ahead = oppc > myc

    best = (-10**18, (0, 0))
    for dx, dy in dir_priority:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in self_cells:
            val = 2.0
        elif (nx, ny) in opp_cells:
            # "Touch" opponent territory: only attractive when behind and close; otherwise avoid.
            d = abs(nx - ox) + abs(ny - oy)
            val = (45.0 - 0.9 * d) if (not opp_ahead) else (5.0 - 1.2 * d)
        elif (nx, ny) in unclaimed:
            a_self = adj_count(self_cells, nx, ny)
            a_opp = adj_count(opp_cells, nx, ny)
            # Prefer growing contiguous regions; avoid being adjacent to opponent sweep.
            base = 18.0 * a_self - 12.0 * a_opp
            # Nudge towards unclaimed with fewer opponent neighbors (lower flip pressure).
            dist_to_opp = abs(nx - ox) + abs(ny - oy)
            pressure = (0.0 if opp_ahead else 1.0) * (2.5 / (1 + dist_to_opp))
            # Also avoid moving into "thin" areas surrounded by opponent.
            val = base + 6.0 * pressure - 2.0 * (a_opp > a_self)
        else:
            val = -1000.0  # unreachable/irrelevant cell types

        # Global slight preference for moving away from opponent if defending; towards if attacking.
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += (-1.0 if opp_ahead else 1.0) * (0.2 * d_opp)

        if val > best[0]:
            best = (val, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]