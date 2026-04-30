def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
        best = None
        bestd = None
        for ddx, ddy in candidates:
            nx, ny = sx + ddx, sy + ddy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles: 
                continue
            d = man(nx, ny, tx, ty)
            if best is None or d < bestd or (d == bestd and (ddx, ddy) < best):
                best = (ddx, ddy); bestd = d
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    # Pick resource where we are relatively closer than opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    if best_res is None:
        return [0, 0]
    return step_towards(best_res[0], best_res[1])