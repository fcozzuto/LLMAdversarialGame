def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def adj_count(cellset, x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in cellset:
                c += 1
        return c

    best = (-10**18, 0, 0)
    for dx, dy, nx, ny in moves:
        if (nx, ny) in self_cells:
            score = 3.0
        elif (nx, ny) in opp_cells:
            d = abs(nx - ox) + abs(ny - oy)
            score = 45.0 - 2.2 * d
            score += 6.0 * (adj_count(self_cells, nx, ny))
        else:
            if (nx, ny) not in unclaimed:
                continue
            a_self = adj_count(self_cells, nx, ny)
            a_opp = adj_count(opp_cells, nx, ny)
            # Prefer expanding our contiguous frontier and avoid letting sweeper wrap us.
            score = 10.0 * a_self - 8.0 * a_opp
            # Mild pull toward nearest unclaimed frontier cell (deterministic via Manhattan).
            score += 0.25 * (w + h) - 0.15 * (abs(nx - sx) + abs(ny - sy))
            score += 0.6 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0.0
            # If close to opponent, only take cells that are well-connected to our territory.
            score -= 4.0 if (abs(nx - ox) + abs(ny - oy) <= 2 and a_self <= 1) else 0.0
        # Tie-break toward staying and then toward opponent-facing direction deterministically.
        score -= 0.01 * (dx * dx + dy * dy)
        score -= 0.0001 * (abs((nx - ox)) + abs((ny - oy)))
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]