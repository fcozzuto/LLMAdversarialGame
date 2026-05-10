def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    moves = [
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def adj_count(cell_set, x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) in cell_set:
                c += 1
        return c

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_cells:
            score = 1.0
        elif (nx, ny) in opp_cells:
            score = 80.0 - 0.6 * dist(nx, ny, ox, oy) + 0.2 * adj_count(opp_cells, nx, ny)
        elif (nx, ny) in unclaimed:
            opp_adj = adj_count(opp_cells, nx, ny)
            self_adj = adj_count(self_cells, nx, ny)
            score = (
                12.0 + 6.0 * opp_adj + 0.6 * self_adj
                - 0.35 * dist(nx, ny, ox, oy)
                + 0.15 * (1 if opp_adj == 0 else 0)
            )
        else:
            score = 0.5  # stepping into unknown treated conservatively

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]