def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    def md(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    if resources:
        best_r = None; best_r_val = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            sd = md((sx, sy), (rx, ry))
            od = md((ox, oy), (rx, ry))
            v = od - sd
            if v > best_r_val or (v == best_r_val and (best_r is None or (rx, ry) < best_r)):
                best_r_val = v; best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w // 2, h // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if resources:
            sd = md((nx, ny), (tx, ty))
            od = md((ox, oy), (tx, ty))
            v = 2 * (od - sd) - md((nx, ny), (ox, oy))
        else:
            v = -md((nx, ny), (ox, oy)) - md((nx, ny), (tx, ty))
        if v > best_val or (v == best_val and (dx, dy) < tuple(best_move)):
            best_val = v; best_move = [dx, dy]

    return best_move