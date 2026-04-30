def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    # Pick target: nearest resource (tie by coords)
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources_sorted = sorted(resources, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
    target = resources_sorted[0]

    # Candidate moves (deterministic order)
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            moves.append((dx, dy))

    best = None
    best_obj = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            obj = 10**9
        else:
            d_self = dist((nx, ny), target)
            d_opp = dist((ox, oy), target)
            # Prefer smaller self distance and larger opponent distance
            obj = d_self * 2 - d_opp
        if best_obj is None or obj < best_obj or (obj == best_obj and (dx, dy) < best):
            best_obj = obj
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]