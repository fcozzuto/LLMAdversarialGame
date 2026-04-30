def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        tx, ty = (W - 1) / 2.0, (H - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = -((nx - tx) ** 2 + (ny - ty) ** 2)
            if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick resource that we can reach sooner than opponent; tie-break by coordinate.
    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        # Higher key is better: advantage first, then prefer closer absolute.
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_res = key, (rx, ry)

    rx, ry = best_res
    # Choose move that reduces distance to target and doesn't step into obstacle.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = dist((nx, ny), (rx, ry))
        # Encourage not only progress but also slight positional tie-break determinism.
        key = (-myd2, abs(nx - rx) + abs(ny - ry) - myd2, dx, dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]] if best else [0, 0]