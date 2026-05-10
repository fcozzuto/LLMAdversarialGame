def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []) or [])
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []) or [])

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    my_corner = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    opp_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def boundary_adj_to_opp(x, y):
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_cells:
                return True
        return False

    # Targeting: first steal/attack near opponent boundary; else claim toward opponent; else expand unclaimed.
    targets = []
    if unclaimed:
        for cell in unclaimed:
            x, y = cell
            if boundary_adj_to_opp(x, y):
                targets.append(cell)
    if not targets and unclaimed:
        targets = list(unclaimed)
    if not targets:
        return [0, 0]

    # Choose deterministic best target
    # Prefer: adjacent to opponent, closer to us, and slightly closer to opponent corner/position.
    def tgt_score(x, y):
        d_us = abs(x - sx) + abs(y - sy)
        d_opp = abs(x - ox) + abs(y - oy)
        adj = 1 if boundary_adj_to_opp(x, y) else 0
        bias = 0.02 * (abs(x - opp_corner[0]) + abs(y - opp_corner[1]))
        return (-1000 * adj) + d_us + 0.6 * d_opp + bias

    tx, ty = min(targets, key=lambda c: tgt_score(c[0], c[1]))

    # Move selection: evaluate immediate neighbor
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in opp_cells:
            val = 1e6 - 2.0 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            val = 5000 - 3.0 * (abs(nx - ox) + abs(ny - oy)) + 0.5 * (boundary_adj_to_opp(nx, ny))
        elif (nx, ny) in self_cells:
            val = -5.0
        else:
            val = -20.0

        # Encourage marching toward target
        val += 10.0 * (-(abs(nx - tx) + abs(ny - ty)))
        # Discourage moving away from opponent generally
        val += 0.01 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]