def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score_cell(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**14
        if (nx, ny) in self_cells:
            return 2.0
        # If we can flip into opponent territory, value higher.
        if (nx, ny) in opp_cells:
            d = abs(nx - ox) + abs(ny - oy)
            return 30.0 - 0.5 * d
        # Otherwise prefer unclaimed; bias toward those adjacent to opponent (edge attacks).
        if (nx, ny) in unclaimed:
            adj_opp = 0
            for dx, dy in neigh8:
                px, py = nx + dx, ny + dy
                if 0 <= px < w and 0 <= py < h and (px, py) in opp_cells:
                    adj_opp += 1
            # Also prefer moving toward opponent when attacking; otherwise toward center.
            cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_center = abs(nx - cx0) + abs(ny - cy0)
            return 8.0 + 2.5 * adj_opp + (1.5 if d_opp < abs(x - ox) + abs(y - oy) else 0.0) - 0.15 * d_center
        # Other cells (should be rare) are weak unless they move toward opponent.
        d_opp = abs(nx - ox) + abs(ny - oy)
        return 0.5 - 0.2 * d_opp

    # Deterministic tie-breaking by fixed move order and lexicographic preference.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        s = score_cell(nx, ny)
        if s > best[0]:
            best = (s, dx, dy)
        elif s == best[0]:
            # Prefer staying when equal; else prefer smaller dx then dy for determinism.
            if (dx, dy) == (0, 0) and (best[1], best[2]) != (0, 0):
                best = (s, dx, dy)
            elif (dx, dy) != (0, 0) and (best[1], best[2]) != (0, 0):
                if (dx, dy) < (best[1], best[2]):
                    best = (s, dx, dy)

    return [int(best[1]), int(best[2])]