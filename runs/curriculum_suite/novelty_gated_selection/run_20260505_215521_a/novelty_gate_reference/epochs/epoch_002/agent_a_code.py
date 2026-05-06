def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target resource that favors winning race: minimize own_d - k*opp_d (k>0)
    if resources:
        k = 0.35
        best_r = None
        best_val = None
        for rx, ry in resources:
            own_d = max(abs(rx - sx), abs(ry - sy))
            opp_d = max(abs(rx - ox), abs(ry - oy))
            val = own_d - k * opp_d
            if best_val is None or val < best_val or (val == best_val and (rx, ry) < best_r):
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    # If target is on obstacle, fall back to center
    if (tx, ty) in obstacles:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        own_dist = max(abs(tx - nx), abs(ty - ny))
        opp_dist = max(abs(tx - nx), abs(ty - ny))  # overwritten below for clarity
        opp_dist = max(abs(tx - nx), abs(ty - ny))  # same target; own_dist already this

        # Race consideration: how close opponent is to the target relative to us after our move
        opp_to_target = max(abs(tx - ox), abs(ty - oy))
        my_to_target = own_dist

        # Additional tie-breaks: prefer moves that reduce distance and keep away from opponent when contested
        score = my_to_target * 1000
        if my_to_target == 0:
            score -= 5000
        # If opponent is already closer to the target, strongly penalize our slowness
        if opp_to_target < my_to_target:
            score += (my_to_target - opp_to_target) * 600
        # Slightly discourage stepping closer to opponent in contested situations
        score += (max(abs(ox - nx), abs(oy - ny))) * 3

        # Deterministic tie-break: lexicographically by (dx,dy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]