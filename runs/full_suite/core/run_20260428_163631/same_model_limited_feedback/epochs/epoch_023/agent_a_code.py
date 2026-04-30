def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves.append((0, 0))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a deterministic target: balance our distance vs opponent distance
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            val = ds - 0.8 * do + 0.01 * (rx + 2 * ry)  # tie-break
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
    else:
        # No resources: drift toward center-ish while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Evaluate all legal moves by how much they reduce our target distance,
    # and slightly account for opponent closeness to the same target.
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = dist((nx, ny), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        # Prefer moves that decrease ds; also avoid moving closer if opponent is already better
        score = ds - 0.6 * do + 0.001 * (nx + 2 * ny)
        # Slightly prefer moving (non-stay) to keep changing policy
        if dx == 0 and dy == 0:
            score += 0.02
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]