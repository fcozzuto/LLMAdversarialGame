def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    grid_obs = observation.get("obstacles") or []
    obs = set()
    for p in grid_obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_tx, best_ty = resources[0][0], resources[0][1]
        best_d = abs(sx - best_tx) + abs(sy - best_ty)
        for r in resources[1:]:
            if r and len(r) >= 2:
                rx, ry = r[0], r[1]
                d = abs(sx - rx) + abs(sy - ry)
                if d < best_d:
                    best_d = d; best_tx = rx; best_ty = ry
    else:
        best_tx, best_ty = w // 2, h // 2

    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        our_to_target = abs(nx - best_tx) + abs(ny - best_ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        key = (our_to_target, -opp_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move