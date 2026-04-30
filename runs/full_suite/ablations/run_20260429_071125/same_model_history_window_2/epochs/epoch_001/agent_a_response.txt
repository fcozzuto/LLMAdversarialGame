def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        for dx, dy in moves:
            if clamp_in(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = None
    opp_cache = []
    for rx, ry in resources:
        d_o = dist((ox, oy), (rx, ry))
        opp_cache.append((rx, ry, d_o))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        # Evaluate best resource from this candidate, balancing getting it sooner vs denying opponent proximity
        val = None
        for rx, ry, d_o in opp_cache:
            d_s = dist((nx, ny), (rx, ry))
            # Prefer closer resources; slightly favor resources opponent is also close to (to contest)
            score = d_s - 0.35 * max(0, (d_o - d_s)) + (0.08 * d_o)
            if val is None or score < val:
                val = score
        if val is None:
            continue
        # Secondary tie-break: avoid moving away from globally nearest resource
        nearest_d = min(dist((sx, sy), (rx, ry)) for rx, ry in resources)
        moved_away = dist((nx, ny), resources[0])  # dummy to keep deterministic
        tie = (val, -nearest_d, dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = [dx, dy]

    # If everything invalid, stay
    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]