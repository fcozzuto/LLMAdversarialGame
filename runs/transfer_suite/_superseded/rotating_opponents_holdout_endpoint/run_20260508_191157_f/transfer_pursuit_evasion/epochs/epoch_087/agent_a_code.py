def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    role = observation.get("self_role", "pursuer")
    pursuer = (role == "pursuer")

    desired_dx = 0 if ox == sx else (1 if ox > sx else -1)
    desired_dy = 0 if oy == sy else (1 if oy > sy else -1)
    if not pursuer:
        desired_dx *= -1
        desired_dy *= -1

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    desired = (desired_dx, desired_dy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_val = None
    for dx, dy in deltas:
        if abs(dx) > 1 or abs(dy) > 1:
            continue
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        away_dist = -man
        score_goal = man if pursuer else away_dist
        # Prefer moves aligned with desired direction; then optimize pursuit/evasion.
        align = abs(dx - desired[0]) + abs(dy - desired[1])
        val = (align, -score_goal if pursuer else score_goal)
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        # If trapped, try staying; otherwise, try any valid move deterministically.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]