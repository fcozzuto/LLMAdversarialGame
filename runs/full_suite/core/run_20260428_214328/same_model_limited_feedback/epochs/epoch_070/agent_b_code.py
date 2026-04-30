def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    # helper
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # choose best resource target based on relative closeness
    best_r = None
    best_val = -10**9
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        val = (-ds) + 0.6 * do  # prefer closer to us and farther from opponent
        if val > best_val:
            best_val = val
            best_r = (rx, ry)
    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = dist((nx, ny), (tx, ty))
        d_op = dist((nx, ny), (ox, oy))
        # primary: get closer to target; secondary: don't walk into opponent
        score = d_target - 0.15 * d_op
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]