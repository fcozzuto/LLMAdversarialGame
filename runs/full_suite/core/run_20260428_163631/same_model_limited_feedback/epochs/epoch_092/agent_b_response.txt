def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set(map(tuple, observation["obstacles"]))
    res_list = [tuple(r) for r in resources if tuple(r) != (x, y)]
    opp_pos = (ox, oy)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not res_list:
            return opp_pos
        best = None
        best_key = None
        for r in res_list:
            rd = dist((x, y), r)
            od = dist(opp_pos, r)
            val = od - rd  # higher means I'm closer
            key = (val, -rd, -r[1], -r[0])  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = r
        return best

    tx, ty = best_target()

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    if best_d is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]