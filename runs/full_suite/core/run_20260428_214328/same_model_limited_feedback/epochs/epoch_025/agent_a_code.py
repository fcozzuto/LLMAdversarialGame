def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    t = observation["turn_index"]
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def dist2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    if resources:
        if t % 2 == 0:
            target = min(resources, key=lambda r: (dist2((sx, sy), r), r[0], r[1]))
        else:
            target = min(resources, key=lambda r: (dist2((ox, oy), r), r[0], r[1]))
        best = None
        best_key = None
        for dx, dy, nx, ny in cand:
            k = (
                dist2((nx, ny), target),
                -dist2((nx, ny), (ox, oy)),
                abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0),
                dx,
                dy,
            )
            if best_key is None or k < best_key:
                best_key, best = k, (dx, dy)
        return [best[0], best[1]]

    # No resources: move to safer position while drifting toward center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for dx, dy, nx, ny in cand:
        k = (
            abs(nx - cx) + abs(ny - cy),
            -dist2((nx, ny), (ox, oy)),
            dx,
            dy,
        )
        if best_key is None or k < best_key:
            best_key, best = k, (dx, dy)
    return [best[0], best[1]]