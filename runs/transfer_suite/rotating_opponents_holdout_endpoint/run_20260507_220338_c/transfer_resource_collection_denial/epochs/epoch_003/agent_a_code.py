def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        move_best = None
        for rx, ry in resources:
            sdist = manhattan(nx, ny, rx, ry)
            odist = manhattan(ox, oy, rx, ry)
            diff = sdist - odist  # negative => we are closer
            val = diff * 1000 + sdist  # primarily beat opponent, then closer
            if move_best is None or val < move_best:
                move_best = val

        if best_val is None or move_best < best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]