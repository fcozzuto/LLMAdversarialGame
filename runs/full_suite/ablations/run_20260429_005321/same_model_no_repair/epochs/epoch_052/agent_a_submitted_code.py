def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_score(px, py, weight_far=0):
        if not resources:
            return 1e9
        # Prefer closer resources; slight bias toward mid-grid for stability
        best = 1e9
        for rx, ry in resources:
            d = abs(rx - px) + abs(ry - py)
            if d < best:
                best = d
        return best + weight_far * (abs(px - (w - 1) / 2) + abs(py - (h - 1) / 2))

    # Predict opponent next step using same local greedy rule (deterministic)
    def opp_next(px, py):
        moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        bestv = 1e18
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not in_bounds(nx, ny) or blocked(nx, ny):
                continue
            v = nearest_score(nx, ny)
            if v < bestv:
                bestv = v
                bestm = (dx, dy)
        return bestm

    opp_dx, opp_dy = opp_next(ox, oy)
    n_ox, n_oy = ox + opp_dx, oy + opp_dy
    if not in_bounds(n_ox, n_oy) or blocked(n_ox, n_oy):
        n_ox, n_oy = ox, oy

    # Evaluate my candidate moves with simple tactical scoring
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = -1e18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        my_d = nearest_score(nx, ny, weight_far=0.05)
        opp_d = nearest_score(n_ox, n_oy, weight_far=0.05)

        # If I move closer to some resource than opponent, reward; else, try to deny.
        if resources:
            # Find closest resource for both
            my_best = 1e9
            opp_best = 1e9
            my_closest = None
            opp_closest = None
            for rx, ry in resources:
                d1 = abs(rx - nx) + abs(ry - ny)
                if d1 < my_best:
                    my_best = d1
                    my_closest = (rx, ry)
                d2 = abs(rx - n_ox) + abs(ry - n_oy)
                if d2 < opp_best:
                    opp_best = d2
                    opp_closest = (rx, ry)

            # Bonus for picking the same closest target with a lead, or for becoming the closest overall.
            lead_bonus = 0.0
            if my_closest == opp_closest:
                lead_bonus = 1.5 * (opp_best - my_best)
            else:
                lead_bonus = 0.6 * (opp_best - my_best)

            # Repel from being too near opponent when not progressing
            near_opp = max(0, 6 - (abs(nx - n_ox) + abs(ny - n_oy)))
            score = 10.0 * (opp_best - my_best) + 2.0 * lead_bonus - 0.25 * near_opp - 0.1 * my_d
        else:
            # No resources: keep safe and central
            score = -0.1 * my_d - 0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]