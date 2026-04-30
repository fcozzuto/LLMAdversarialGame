def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    adj8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx if dx >= 0 else -dx + (dy if dy >= 0 else -dy)

    def adj_obs(x, y):
        c = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    # If on resource, capture by staying.
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    if not resources:
        # With no resources, drift away from opponent while staying legal.
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_o = abs(nx - ox) + abs(ny - oy)
            penalty = adj_obs(nx, ny)
            val = (-d_o, penalty, dx*dx + dy*dy)
            if val < best:
                best = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose a move that maximizes advantage toward a reachable resource.
    best_val = (-10**18, 10**18, 10**18)
    best_move = (0, 0)
    res_list = [(rx, ry) for rx, ry in resources]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        a = 10**18
        b = 10**18
        best_resource_score = -10**18
        for rx, ry in res_list:
            d_s = abs(nx - rx) + abs(ny - ry)
            d_o = abs(ox - rx) + abs(oy - ry)
            # Prefer resources where self is closer (or will be closer after move).
            advantage = (d_o - d_s)
            # Penalize being stuck near obstacles; slightly prefer lower total distance.
            score = advantage * 100 - d_s - 3 * adj_obs(nx, ny)
            # Encourage taking very close resources even if advantage is small.
            if d_s == 0:
                score += 10**6
            if score > best_resource_score:
                best_resource_score = score
                a = d_s
                b = d_o

        # Secondary criteria: maximize self closeness advantage and distance from opponent when not advantaged.
        opp_dist = abs(nx - ox) + abs(ny - oy)
        dist_term = a - b  # smaller is better (self closer than opponent)
        # If overall not advantaged, prioritize staying away from opponent.
        away = 1 if dist_term > 0 else 0
        val = (-best_resource_score, away * (-opp_dist), dist_term + 0.01 * (dx*dx + dy*dy), dx, dy)
        # Deterministic tie-break by val components (and move order via dx,dy).
        if val < (-best_val[0], -best_val[1], -best_val[2], 0, 0):
            best_val = best_val  # no-op, keep structure consistent
        # Compare using primary tuple directly
        if (val[0], val[1], val[2], val[3], val[4]) < (best_val[0], best_val[1], best_val[2], best_move[0], best_move[1]):
            best_val = (val[0], val[1], val[2])
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]