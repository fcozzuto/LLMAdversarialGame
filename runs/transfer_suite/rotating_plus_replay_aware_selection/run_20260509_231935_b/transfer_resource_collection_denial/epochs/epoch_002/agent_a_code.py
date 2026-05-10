def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    obs_list = list(obstacles_list)
    have_obs = len(obs_list) > 0

    def obstacle_penalty(nx, ny):
        if not have_obs:
            return 0
        best = None
        for px, py in obs_list:
            d = (nx - px) * (nx - px) + (ny - py) * (ny - py)
            if best is None or d < best:
                best = d
        return 0 if best is None else (1 if best == 0 else 0.01 * best)

    best_delta = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that best advances us while keeping opponent farther.
        local_best = None
        local_t = None
        for rx, ry in resources:
            ds = dist2((nx, ny), (rx, ry))
            do = dist2((ox, oy), (rx, ry))
            # Lower is better: prioritize small ds, large do.
            # Add a tiny lexicographic tie-break on resource location for determinism.
            key = (ds + 0.7 * do, rx, ry)
            if local_best is None or key < local_best:
                local_best = key
                local_t = (rx, ry)

        # Also penalize sitting near obstacles slightly to avoid traps.
        key = (local_best[0], local_best[1], local_best[2], obstacle_penalty(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]