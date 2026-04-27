def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds <= do, -ds, do, ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
                d = dist((nx, ny), (tx, ty))
                block = dist((nx, ny), (ox, oy)) == 0
                candidates.append((d, block, dx, dy, nx, ny))
    # Prefer moves that reduce distance to target; if tied, avoid blocking/joining opponent; deterministic tie-break by dx,dy.
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    _, _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]