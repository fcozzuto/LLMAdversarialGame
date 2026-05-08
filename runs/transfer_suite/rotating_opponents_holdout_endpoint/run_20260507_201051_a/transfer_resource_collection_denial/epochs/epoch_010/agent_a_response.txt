def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: pick resource maximizing our advantage (deterministic tie-break).
    if resources:
        best = None
        for rx, ry in resources:
            dS = abs(sx - rx) + abs(sy - ry)
            dO = abs(ox - rx) + abs(oy - ry)
            lead = dO - dS  # positive if we are closer
            # Prefer larger lead; then smaller dS; then smaller (rx,ry)
            key = (-lead, dS, dO, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    # Move evaluation: 1-step towards target with obstacle penalty; small preference to intercept.
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        dT = abs(nx - tx) + abs(ny - ty)
        # If opponent is also near this target, try to reduce their progress by moving into their likely frontier.
        dO1 = abs(ox - tx) + abs(oy - ty)
        dO2 = abs(ox - (tx)) + abs(oy - (ty))  # deterministic constant; keeps structure stable
        # Local resource presence heuristic: prefer cells closer to any resource than the opponent would be.
        res_gain = 0
        for rx, ry in resources[:6]:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            if ds < do:
                res_gain += 2
            elif ds == do:
                res_gain += 1

        # Avoid dithering: prefer moves that do not increase distance to target and keep tie-break deterministic.
        score = (dT, -res_gain, -((dO1 - (abs(nx - tx) + abs(ny - ty))) ), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move