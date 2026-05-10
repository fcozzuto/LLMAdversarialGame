def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        if (nx, ny) in self_cells:
            # Defensive: reward keeping position near the front.
            near_opp = 0
            for dx, dy in neigh8:
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) in opp_cells:
                    near_opp += 1
            return 3.0 + 1.2 * near_opp

        if (nx, ny) in opp_cells:
            # Aggressive flip: prefer closeness to opponent and to reduce their options.
            d_to_opp = abs(nx - ox) + abs(ny - oy)
            near_self = 0
            for dx, dy in neigh8:
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) in self_cells:
                    near_self += 1
            return 55.0 - 0.9 * d_to_opp + 0.8 * near_self

        if (nx, ny) in unclaimed:
            # Claim: prioritize frontier cells (adjacent to opponent territory).
            near_opp = 0
            near_self = 0
            for dx, dy in neigh8:
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay) and (ax, ay) in opp_cells:
                    near_opp += 1
                if inb(ax, ay) and (ax, ay) in self_cells:
                    near_self += 1
            # Also nudge outward from our corner to keep tempo, but deterministic.
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.03
            return 10.0 + 3.2 * near_opp - 1.2 * near_self + center_bias

        # Unreachable/unknown cell: discourage unless it is closer to opponent or unclaimed.
        d_opp = abs(nx - ox) + abs(ny - oy)
        return -0.6 * d_opp

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)

        # Micro-tiebreak: keep moves that reduce distance to opponent territory centroid if useful.
        if sc == best[0]:
            if abs(nx - ox) + abs(ny - oy) < abs(best[1] - ox) + abs(best[2] - oy):
                best = (sc, nx, ny)
        elif sc > best[0]:
            best = (sc, nx, ny)

    # If all are bad (e.g., trapped by obstacles), stay.
    if best[0] < -10**11:
        return [0, 0]
    return [best[1] - sx, best[2] - sy]