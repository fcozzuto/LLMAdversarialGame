def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Race heuristic: prefer resources where we would be closer than opponent.
        my_best_delta = -10**18
        my_best_dist = 10**18
        for rx, ry in resources:
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            delta = opp_d - my_d  # positive => our advantage
            if delta > my_best_delta or (delta == my_best_delta and my_d < my_best_dist):
                my_best_delta = delta
                my_best_dist = my_d

        # If no resources, just drift away a bit while staying safe.
        if not resources:
            val = abs(nx - ox) + abs(ny - oy)
        else:
            # Higher is better: advantage first, then closeness to the chosen advantageous target.
            val = my_best_delta * 1000 - my_best_dist

        # Mild anti-stacking: avoid moving into opponent proximity if all else ties.
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += d_opp * 0.01

        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best if best is not None else [0, 0]