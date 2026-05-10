def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(cset, x, y):
        c = 0
        for dx, dy in neigh8:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in cset:
                c += 1
        return c

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        dcen = abs(x - cx) + abs(y - cy)
        dpop = abs(x - ox) + abs(y - oy)
        adj_self = adj_count(self_cells, x, y)
        base = 0.55 * (10.0 - dcen) + 0.35 * adj_self - 0.12 * dpop
        if (x, y) in opp_cells:
            return 120.0 - 0.9 * dpop + 0.25 * adj_self
        if (x, y) in unclaimed:
            return base + 3.5 + 0.15 * (dcen < 6.0) - 0.25 * (dpop <= 1)
        if (x, y) in self_cells:
            return base + 1.2
        return base - 0.5

    best = None
    best_s = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]