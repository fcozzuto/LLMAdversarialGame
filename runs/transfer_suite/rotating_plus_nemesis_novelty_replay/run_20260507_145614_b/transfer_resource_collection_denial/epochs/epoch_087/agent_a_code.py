def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2; a = -a if a < 0 else a
        b = y1 - y2; b = -b if b < 0 else b
        return a if a > b else b

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    targets = resources
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_best = 10**9
        op_best = 10**9
        for rx, ry in targets:
            d = cheb(nx, ny, rx, ry)
            if d < my_best:
                my_best = d
            od = cheb(ox, oy, rx, ry)
            if od < op_best:
                op_best = od
        mid = (w - 1) / 2.0
        prefer_side = 1 if (nx <= mid) == (sx <= mid) else 0
        val = (op_best - my_best) * 100 + (prefer_side * 3) - (my_best)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move