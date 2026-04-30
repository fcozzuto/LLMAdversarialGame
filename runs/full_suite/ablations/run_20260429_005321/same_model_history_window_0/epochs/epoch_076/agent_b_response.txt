def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (do - ds, -ds, -((rx + ry) % 7))  # prefer being closer; tie-break deterministically
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d = dist((nx, ny), (tx, ty))
        # prefer reducing distance; tie-break toward also being closer than opponent
        do = dist((ox, oy), (tx, ty))
        key = (-d, (do - d), -(abs(dx) + abs(dy)), -((nx + ny) % 5))
        if best_d is None or key > best_d:
            best_d = key
            best_move = [dx, dy]

    if best_d is None:
        return [0, 0]
    return best_move