def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = neigh8

    best_score = -10**18
    best_move = (0, 0)

    def cell_value(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**15
        if (nx, ny) in self_cells:
            return 1.5
        if (nx, ny) in opp_cells:
            d = abs(nx - ox) + abs(ny - oy)
            return 60.0 - 0.7 * d
        if (nx, ny) in unclaimed:
            adj_opp = 0
            for dx, dy in neigh8:
                px, py = nx + dx, ny + dy
                if 0 <= px < w and 0 <= py < h and (px, py) in opp_cells:
                    adj_opp += 1
            adj_self = 0
            for dx, dy in neigh8:
                px, py = nx + dx, ny + dy
                if 0 <= px < w and 0 <= py < h and (px, py) in self_cells:
                    adj_self += 1
            dopp = abs(nx - ox) + abs(ny - oy)
            border = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            return 18.0 + 7.0 * adj_opp + 0.8 * adj_self + (5.0 if border else 0.0) - 0.08 * dopp
        return 0.0

    # Prefer deterministic tie-breaking by fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_value(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) == (0, 0) and best_move != (0, 0)):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]