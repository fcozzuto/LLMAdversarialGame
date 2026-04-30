def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set((x, y) for x, y in obstacles)
    res_set = set((x, y) for x, y in resources)

    if (sx, sy) in res_set:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clip(p):
        x, y = p
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    # Pick resource that favors us being closer than the opponent (deterministic).
    best_r = None
    best_metric = None
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        my_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        metric = my_d - opp_d
        if best_metric is None or metric < best_metric or (metric == best_metric and my_d < dist((sx, sy), best_r)):
            best_metric = metric
            best_r = (rx, ry)
    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    opp_d_target = dist((ox, oy), (tx, ty))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = clip((sx + dx, sy + dy))
        if (nx, ny) in obst:
            continue
        my_d_after = dist((nx, ny), (tx, ty))
        # Prefer reducing our distance while also keeping/creating advantage vs opponent.
        val = my_d_after - opp_d_target
        if best_val is None or val < best_val or (val == best_val and my_d_after < dist((sx, sy), (tx, ty))):
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]