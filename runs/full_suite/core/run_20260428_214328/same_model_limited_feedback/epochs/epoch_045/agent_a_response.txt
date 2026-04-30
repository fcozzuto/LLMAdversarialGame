def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        best = None
        best_val = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            val = dist((nx, ny), (ox, oy))  # run away
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Choose resource that is relatively safer: opponent farther than us.
    best_r = None
    best_metric = -10**18
    for r in resources:
        if tuple(r) in obstacles:
            continue
        r = tuple(r)
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        metric = (do - ds) * 10 - ds  # prioritize stealing/denying
        # tie-break deterministically by coordinates
        if metric > best_metric or (metric == best_metric and r < best_r):
            best_metric = metric
            best_r = r

    tx, ty = best_r
    # Move toward target while keeping away from opponent and avoiding obstacles.
    # Deterministic tie-break by fixed deltas order.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        val = -d_t * 3 + d_o  # primarily close target, secondarily separate
        if (nx, ny) == (tx, ty):
            val += 10000
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]