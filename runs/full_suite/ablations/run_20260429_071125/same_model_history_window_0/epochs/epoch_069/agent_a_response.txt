def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    obst = set((p[0], p[1]) for p in obstacles)
    opp_dist = abs(sx - ox) + abs(sy - oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    if not resources:
        # No resources: move to maximize distance from opponent while staying valid
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            score = d
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue

        # Choose the best resource matchup from the candidate position
        my_best = -10**18
        for rx, ry in resources:
            d_my = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)
            # If we can arrive not later than opponent, prioritize; otherwise penalize
            if d_my <= d_opp:
                s = -d_my + 5 * (d_opp - d_my)
            else:
                s = -d_my - 3 * (d_my - d_opp)
            # Also slight preference for actually moving onto a resource
            if d_my == 0:
                s += 20
            if s > my_best:
                my_best = s

        # Add opponent proximity pressure (encourage breaking contact if not winning races)
        d_new_opp = abs(nx - ox) + abs(ny - oy)
        score = my_best + (0.25 * d_new_opp if d_new_opp >= opp_dist else -0.1 * (opp_dist - d_new_opp))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]