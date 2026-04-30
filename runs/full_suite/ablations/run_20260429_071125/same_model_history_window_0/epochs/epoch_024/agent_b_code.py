def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance for 8-dir

    # If standing on a resource, just drift toward next best.
    target = None
    best = None

    if resources:
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner; break ties by closer to center and then x/y.
            center = (w // 2, h // 2)
            dc = dist((rx, ry), center)
            score = (ds - do, ds, dc, rx, ry)
            if best is None or score < best:
                best = score
                target = (rx, ry)
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order already defined above.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dself = dist((nx, ny), (tx, ty))
        # Avoid letting opponent get closer to our target than we do.
        dopp = dist((ox, oy), (tx, ty))
        # Also slight repulsion from obstacles neighborhood to reduce getting stuck.
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obstacles:
                    near_obs += 1

        val = (dself, near_obs, (dself - dopp), abs((nx - w // 2)) + abs((ny - h // 2)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]