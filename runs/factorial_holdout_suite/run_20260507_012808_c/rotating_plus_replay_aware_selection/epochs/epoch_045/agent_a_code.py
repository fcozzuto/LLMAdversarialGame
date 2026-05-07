def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res = [tuple(r) for r in resources]
    res_set = set(res)

    def dist(x, y, rx, ry):
        return abs(rx - x) + abs(ry - y)

    # If no visible resources, drift toward center to reduce future distances.
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    opp_min = 10**9
    my_min = 10**9
    for rx, ry in res:
        d1 = dist(sx, sy, rx, ry)
        d2 = dist(ox, oy, rx, ry)
        if d1 < my_min: my_min = d1
        if d2 < opp_min: opp_min = d2

    best = (0, 0)
    best_val = -10**18

    # Evaluate moves by best "advantage" resource we can reach sooner than opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pickup = 1 if (nx, ny) in res_set else 0

        # Best advantage after this move:
        # advantage = (opp_dist - my_dist) with strong drive to close and pick up.
        best_adv = -10**9
        best_goal_dist = 10**9
        for rx, ry in res:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            adv = op_d - my_d
            # Tie-break toward closer resources for us.
            if adv > best_adv or (adv == best_adv and my_d < best_goal_dist):
                best_adv = adv
                best_goal_dist = my_d

        # Additional shaping: if we are currently behind, prioritize stealing nearest resource to us vs opponent.
        # If ahead, prioritize reducing our remaining distance.
        score = 0
        score += 30 * pickup
        score += 8 * best_adv
        score += -1.2 * best_goal_dist

        # If opponent is closer to the same nearest resource, encourage movement that reduces that gap less.
        # (Approx: compare nearest distances to our position after move.)
        my_after_min = best_goal_dist
        # If opponent already closer (small), we try to swing advantage.
        score += -0.8 * max(0, my_after_min - opp_min)

        # Deterministic preference order when values tie: fewer movement steps (favor staying) slightly.
        if score > best_val or (score == best_val and (abs(dx) + abs(dy), dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            best_val = score
            best = (dx, dy)

    return [best[0], best[1]]