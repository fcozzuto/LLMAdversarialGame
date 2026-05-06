def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs_set = { (p[0], p[1]) for p in obstacles }
    resources = observation.get("resources", [])

    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            cand = (d, rx, ry)
            if best is None or cand < best:
                best = cand
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_obj = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            nx, ny = sx, sy
        dist_t = (tx - nx) ** 2 + (ty - ny) ** 2
        dist_o = (ox - nx) ** 2 + (oy - ny) ** 2
        obj = dist_t - 0.15 * dist_o
        if (nx, ny) in obs_set:
            obj += 1e9
        if best_obj is None or obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]