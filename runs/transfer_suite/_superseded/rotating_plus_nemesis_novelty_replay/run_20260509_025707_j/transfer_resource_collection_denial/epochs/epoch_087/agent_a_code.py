def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    tr = observation.get("turns_remaining", 0)
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Compute score for the best resource we could aim for this move
        local_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Big win potential: get to a resource at least as fast as opponent (or faster)
            gap = opp_d - my_d
            # Tie-break: prefer closer and slightly earlier as turns run out
            urgency = (12 - tr) if tr is not None else 0
            time_pref = -my_d + (urgency * 0.05)
            # If both can reach, try to deny: maximize (gap) and minimize distance
            val = gap * 10 + time_pref - (my_d * 0.2)
            if val > local_best:
                local_best = val

        # Add a small "intercept" effect: increase opponent distance while moving (prevents shadow-capture)
        opp_dist = man(nx, ny, ox, oy)
        val = local_best + opp_dist * 0.03

        if val > bestv:
            bestv = val
            best = (dx, dy)
        elif val == bestv and best is not None:
            # Deterministic tie-break: prefer moves that reduce our distance to opponent
            if man(nx, ny, ox, oy) > man(sx, sy, ox, oy):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]