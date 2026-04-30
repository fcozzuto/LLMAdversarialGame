def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((a, b) for a, b in obstacles)
    targets = resources if resources else []
    if not targets:
        # No resources: move to improve position vs center
        cx, cy = observation.get("grid_width", 8) // 2, observation.get("grid_height", 8) // 2
        tx, ty = cx, cy
    else:
        def dist(a, b, c, d):
            return abs(a - c) + abs(b - d)
        best = None
        for rx, ry in targets:
            sd = dist(x, y, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            # Prefer winning advantage, then closer to target
            key = (adv, -sd, -dist(x, y, ox, oy))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        _, tx, ty = best
    dx = 0
    dy = 0
    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cur_to_t = abs(x - tx) + abs(y - ty)
    best_move = (0, 0)
    best_score = (-10**9, -10**9)
    for mx, my in deltas:
        nx, ny = x + mx, y + my
        if (nx, ny) in obs_set or nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        step_improve = cur_to_t - nd
        # Tie-break: also try to avoid stepping toward opponent too much
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = (step_improve, opp_dist)
        if score > best_score:
            best_score = score
            best_move = (mx, my)
    return [int(best_move[0]), int(best_move[1])]