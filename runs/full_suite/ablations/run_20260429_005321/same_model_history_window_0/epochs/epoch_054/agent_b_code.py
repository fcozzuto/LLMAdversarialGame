def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources", [])
    target = None
    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            myd = (x - rx) * (x - rx) + (y - ry) * (y - ry)
            opd = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            key = (myd - opd, myd, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        opd = (ox - tx) * (ox - tx) + (oy - ty) * (oy - ty)
        dist_adv = myd - opd
        step_cost = abs(dx) + abs(dy)
        score = (dist_adv, myd, -opd, step_cost, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move