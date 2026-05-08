def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def has_adj(cell_set, x, y):
        for dx, dy in adj:
            if (x + dx, y + dy) in cell_set:
                return True
        return False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        c_un = 1 if (nx, ny) in unclaimed else 0
        c_self = 1 if (nx, ny) in self_t else 0
        c_opp = 1 if (nx, ny) in opp_t else 0

        adj_self = 1 if has_adj(self_t, nx, ny) else 0
        adj_opp = 1 if has_adj(opp_t, nx, ny) else 0

        # Move selection: deny opponent expansion by occupying unclaimed near them,
        # while avoiding stepping into hot opponent edges unless flipping helps.
        sc = 0.0
        sc += c_un * 3.5
        sc += c_self * 0.6
        if c_opp:
            sc += 2.2  # flipping gives control; should be valuable
        sc += adj_self * 1.4
        sc -= adj_opp * (2.4 if not c_opp else 0.6)

        # Prefer moving toward our territory "mass" (stable growth) deterministically.
        # Use count of self neighbors as a tie-breaker.
        self_n = 0
        opp_n = 0
        for adx, ady in adj:
            px, py = nx + adx, ny + ady
            if (px, py) in self_t:
                self_n += 1
            if (px, py) in opp_t:
                opp_n += 1
        sc += self_n * 0.15
        sc -= opp_n * 0.25

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            # deterministic tie-break: prefer closer to center, then staying still
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            d_best = abs((sx + best[0]) - cx) + abs((sy + best[1]) - cy)
            d_new = abs(nx - cx) + abs(ny - cy)
            if d_new < d_best or (d_new == d_best and (dx, dy) == (0, 0) and best != (0, 0)):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]