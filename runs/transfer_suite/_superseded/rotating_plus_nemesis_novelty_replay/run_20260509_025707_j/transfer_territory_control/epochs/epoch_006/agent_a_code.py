def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    target_x = corner[0] if corner[0] != sx else (w - 1 if ox < w // 2 else 0)
    target_y = corner[1] if corner[1] != sy else (h - 1 if oy < h // 2 else 0)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_frontier_value(x, y):
        # Frontier: unclaimed cells near our territory edge or opponent territory
        adj_self = 0
        adj_opp = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                if (nx, ny) in self_cells:
                    adj_self += 1
                if (nx, ny) in opp_cells:
                    adj_opp += 1
        return 1.5 * adj_self + 2.5 * adj_opp

    best_score = -10**18
    best_move = (0, 0)

    # If we have much more area, defend by biasing away from opponent; else expand/contest.
    lead = observation.get("self_territory_count", len(self_cells)) - observation.get("opponent_territory_count", len(opp_cells))
    defend = 1 if lead >= 6 else 0

    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_cells:
            d = abs(nx - ox) + abs(ny - oy)
            score = 80.0 - 0.35 * d
            if defend:
                score -= 5.0  # still flip, but less aggressively when leading
        elif (nx, ny) in unclaimed:
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_tgt = abs(nx - target_x) + abs(ny - target_y)
            frontier = cell_frontier_value(nx, ny)
            score = 35.0 + 5.0 * frontier - 0.6 * d_opp - 0.15 * d_tgt
            if defend:
                # Reduce risk of letting opponent sweep back: stay nearer to our territory
                d_self = abs(nx - sx) + abs(ny - sy)
                score -= 0.25 * d_self
        else:
            # Staying on/near our territory is OK; prefer moves that bring us toward target/opponent frontier
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_tgt = abs(nx - target_x) + abs(ny - target_y)
            frontier = cell_frontier_value(nx, ny)
            score = 10.0 + 1.0 * frontier - 0.25 * d_opp - 0.05 * d_tgt

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]