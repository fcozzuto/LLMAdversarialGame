def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    dxs = (-1, 0, 1)
    candidates = [(dx, dy) for dx in dxs for dy in dxs]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            adv = do - ds
            key = (adv, -ds)  # maximize advantage, then prefer smaller ds
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds1 = dist((nx, ny), (tx, ty))
        do1 = dist((ox, oy), (tx, ty))
        # prefer getting closer to target and keeping opponent farther from it
        val = (-ds1) + (0.25 * do1) + (0.05 * (ds1 == 0))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]