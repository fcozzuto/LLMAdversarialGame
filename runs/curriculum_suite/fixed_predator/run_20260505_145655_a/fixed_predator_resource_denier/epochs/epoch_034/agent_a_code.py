def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = -10**18
        opp_best = -10**18
        # Evaluate: (1) maximize advantage for a resource we pursue, (2) minimize opponent's advantage/delivery.
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            delta = oppd - selfd  # positive => we are closer
            # Encourage moving toward nearer contested resources and staying competitive.
            sc = delta * 5 - selfd * 0.5
            if sc > my_best:
                my_best = sc
            # Opponent delivery: penalize states that leave a resource where opponent is strongly favored.
            opp_sc = delta * 3 + selfd * 0.2  # if delta negative large magnitude, bad
            if opp_sc > opp_best:
                opp_best = opp_sc

        # Net: pursue our best while also reducing opponent's strongest remaining opportunity.
        # If opponent is currently winning a resource set, deny it more.
        # Approximate by current best advantage for opponent (using our current position).
        cur_opp_adv = -10**18
        for rx, ry in resources:
            selfd0 = abs(sx - rx) + abs(sy - ry)
            oppd0 = abs(ox - rx) + abs(oy - ry)
            d0 = oppd0 - selfd0
            cur_opp_adv = max(cur_opp_adv, d0)
        pressure = 1.0 + (cur_opp_adv if cur_opp_adv > 0 else 0.0) * 0.25

        net = my_best - opp_best * pressure + (0 if (nx, ny) in obstacles else 0)
        if net > best_score:
            best_score = net
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]