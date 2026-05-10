def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**15
        if (x, y) in self_cells:
            return 1.0
        # prefer flipping opponent territory
        if (x, y) in opp_cells:
            d_opp = abs(x - ox) + abs(y - oy)
            d_ctr = abs(x - cx) + abs(y - cy)
            return 120.0 - 0.6 * d_opp + 0.15 * d_ctr
        # prefer taking unclaimed near opponent boundary, but push toward edges (anti-center)
        if (x, y) in unclaimed:
            adj_opp = 0
            adj_self = 0
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_cells:
                    adj_opp += 1
                if (nx, ny) in self_cells:
                    adj_self += 1
            d_ctr = abs(x - cx) + abs(y - cy)
            d_opp = abs(x - ox) + abs(y - oy)
            return 20.0 + 7.0 * adj_opp + 0.5 * adj_self + 0.25 * d_ctr - 0.15 * d_opp
        return -1.0

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]