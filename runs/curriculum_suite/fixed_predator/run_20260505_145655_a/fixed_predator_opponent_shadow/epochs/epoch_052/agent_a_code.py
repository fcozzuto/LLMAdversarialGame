def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_value(px, py):
        best = -10**18
        for tx, ty in resources:
            my_d = abs(tx - px) + abs(ty - py)
            opp_d = abs(tx - ox) + abs(ty - oy)
            # Prefer states where we are closer than opponent; also quick progress.
            v = (opp_d - my_d) * 1000 - my_d + 0.01 * opp_d
            if v > best:
                best = v
        return best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            score = -10**18 // 2
        else:
            score = best_value(nx, ny)
            # Small tie-break: avoid stepping away from selected direction too much.
            score -= 0.001 * (abs(ox - nx) + abs(oy - ny) - abs(ox - x) - abs(oy - y))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move