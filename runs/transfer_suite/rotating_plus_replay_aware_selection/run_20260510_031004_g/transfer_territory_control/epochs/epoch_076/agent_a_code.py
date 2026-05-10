def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def center_dist(x, y):
        return abs(x - cx) + abs(y - cy)

    # Deterministic tie-break order
    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx, dy) != (0, 0):
                moves.append((dx, dy))

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic value for immediate move
        if (nx, ny) in opp_terr:
            val = 1000 - 2 * center_dist(nx, ny) + 0.5 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in unclaimed:
            val = 300 - 3 * center_dist(nx, ny) - 0.2 * (abs(nx - ox) + abs(ny - oy))
        elif (nx, ny) in self_terr:
            val = 50 - 2 * center_dist(nx, ny)
        else:
            val = 80 - 2 * center_dist(nx, ny)

        # Slight preference to approach cells near opponent front line
        val += -0.05 * (abs(nx - ox) + abs(ny - oy))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]