def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_terr = set(tuple(p) for p in observation.get("self_territory", []) or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []) or [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_unclaimed(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    def dist_to_opp(x, y):
        return abs(ox - x) + abs(oy - y)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0.0
        if (nx, ny) in self_terr:
            score += 1.0
        elif (nx, ny) in unclaimed:
            score += 3.0
        elif (nx, ny) in opp_terr:
            score += 6.0

        score += 0.65 * adj_unclaimed(nx, ny)

        # Pressure: contest the center area and the opponent claim region
        score += 0.40 * (10.0 - ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)))
        score += 0.30 * (-dist_to_opp(nx, ny))

        # Small tie-breaker: prefer moves that reduce Manhattan distance to center
        score += 0.001 * (-(abs(nx - cx) + abs(ny - cy)))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]