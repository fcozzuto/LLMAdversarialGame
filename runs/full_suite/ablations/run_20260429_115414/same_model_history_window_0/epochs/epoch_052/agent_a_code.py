def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            key = (do - ds, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        oppdist = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        val = -dist + 0.03 * oppdist
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]