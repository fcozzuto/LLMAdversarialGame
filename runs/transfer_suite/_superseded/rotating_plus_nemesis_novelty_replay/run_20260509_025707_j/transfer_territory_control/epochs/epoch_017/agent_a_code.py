def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in observation.get("obstacles", [])}
    self_cells = {(p[0], p[1]) for p in observation.get("self_territory", [])}
    opp_cells = {(p[0], p[1]) for p in observation.get("opponent_territory", [])}
    unclaimed = {(p[0], p[1]) for p in observation.get("unclaimed_cells", [])}
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def value(nx, ny):
        if not inb(nx, ny):
            return -10**9
        if (nx, ny) in self_cells:
            return 5.0
        if (nx, ny) in opp_cells:
            return 80.0 - 0.8 * (abs(nx - ox) + abs(ny - oy))
        if (nx, ny) in unclaimed:
            adj_opp = 0
            adj_self = 0
            for dx, dy in neigh8:
                ax, ay = nx + dx, ny + dy
                if 0 <= ax < w and 0 <= ay < h:
                    if (ax, ay) in opp_cells:
                        adj_opp += 1
                    if (ax, ay) in self_cells:
                        adj_self += 1
            center_bias = -0.03 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            return 20.0 + 6.0 * adj_opp + 2.0 * adj_self + center_bias
        # empty unknown: prefer moving toward opponent/center slightly
        return -0.01 * (abs(nx - ox) + abs(ny - oy))

    best = None
    best_v = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        v = value(nx, ny)
        if v > best_v or (v == best_v and (dx, dy) < (best[0], best[1]) if best else True):
            best_v = v
            best = (dx, dy)
    return [best[0], best[1]]