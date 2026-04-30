def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def clamp_moves():
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    moves.append((dx, dy))
        return moves

    valid_moves = clamp_moves()
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer resources where we are closer than opponent; otherwise nearest resource.
    best = None
    best_score = -10**9
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Strong bias for getting to a resource first; also prefer closer overall.
        score = (do - ds) * 20 - ds
        # If resource is on our square, just stay (engine will handle pickup).
        if ds == 0:
            score = 10**9
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Choose next step that minimizes distance to target.
    best_move = (0, 0)
    best_d = dist((sx, sy), (tx, ty))
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), (tx, ty))
        if d < best_d:
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]