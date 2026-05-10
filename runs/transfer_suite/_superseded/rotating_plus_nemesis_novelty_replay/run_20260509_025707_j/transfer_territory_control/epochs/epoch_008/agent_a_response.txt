def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = neigh8

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_to_opp(nx, ny):
        c = 0
        for dx, dy in neigh8:
            px, py = nx + dx, ny + dy
            if 0 <= px < w and 0 <= py < h and (px, py) in opp_cells:
                c += 1
        return c

    def score_cell(nx, ny):
        if not inb(nx, ny):
            return -10**14
        if (nx, ny) in self_cells:
            return 1.5  # avoid unnecessary flips
        if (nx, ny) in opp_cells:
            d = abs(nx - ox) + abs(ny - oy)
            return 80.0 - 1.0 * d + 3.0 * adj_to_opp(nx, ny)
        if (nx, ny) in unclaimed:
            d = abs(nx - ox) + abs(ny - oy)
            edge_bonus = 6.0 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0.0
            return 25.0 - 0.4 * d + 2.0 * adj_to_opp(nx, ny) + edge_bonus
        # default (shouldn't happen)
        return 0.0

    best_s = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        s = score_cell(nx, ny)
        # Deterministic tie-break: prefer staying if equal? else lexicographic
        if s > best_s or (s == best_s and (dx, dy) < best_move):
            best_s = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]