def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def val(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - cx) + abs(ny - cy)
        base = 0.0
        if (nx, ny) in self_cells:
            base = 1.0
        elif (nx, ny) in opp_cells:
            base = 40.0 - 0.9 * d_opp
        elif (nx, ny) in unclaimed:
            adj_opp = 0
            for ddx, ddy in neigh8:
                px, py = nx + ddx, ny + ddy
                if inb(px, py) and (px, py) in opp_cells:
                    adj_opp += 1
            base = 18.0 + 2.5 * adj_opp - 0.6 * d_opp - 0.15 * d_center
        else:
            base = 3.0 - 0.2 * d_center

        adj_self = 0
        for ddx, ddy in neigh8:
            px, py = nx + ddx, ny + ddy
            if inb(px, py) and (px, py) in self_cells:
                adj_self += 1
        base += 0.3 * adj_self

        # Mild anti-trap: prefer positions with more free neighboring options
        free = 0
        for ddx, ddy in neigh8:
            px, py = nx + ddx, ny + ddy
            if inb(px, py) and (px, py) not in obstacles:
                free += 1
        base += 0.05 * free
        return base

    best_v = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = val(nx, ny)
        if v > best_v:
            best_v = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]