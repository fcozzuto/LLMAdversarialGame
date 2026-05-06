def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = None
    best_key = None
    for r in resources:
        rx, ry = r
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        # Prefer resources I can reach no later than opponent; otherwise still prefer closer advantage.
        key = (opd - myd, -myd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        # Also slightly prefer moves that increase my distance to opponent (minor blocking).
        od = dist((nx, ny), (ox, oy))
        mkey = (-myd, od, dx, dy)  # minimize myd, then maximize od, deterministic tie-break
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]