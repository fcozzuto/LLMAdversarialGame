def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def blocked(nx, ny):
        return (nx, ny) in obstacles or nx < 0 or nx >= w or ny < 0 or ny >= h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [-sign(x - ox), -sign(y - oy)]

    # One-step lookahead: choose move that maximizes best resource-lead score.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if blocked(nx, ny):
            nx, ny = x, y

        # Secondary term: slightly prefer moves that reduce distance to opponent when neutral.
        opp_delta = man(nx, ny, ox, oy)

        local_best = -10**18
        for tx, ty in resources:
            d_me = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me  # higher is better
            # Encourage securing resources we can reach earlier, but still make progress on all.
            s = lead * 1000 - d_me + 0.01 * d_opp
            # Tiny deterministic bias to spread targets: favor lower (tx,ty) when scores tie.
            s -= (tx * 0.000001 + ty * 0.0000005)
            if s > local_best:
                local_best = s

        # If resources are evenly valued, push to intercept (shadow) by closing distance a bit.
        score = local_best + 0.03 * (7 - opp_delta)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]