def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def step_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    opp_next = []
    best = None
    best_val = None

    # Evaluate each move by choosing the best immediate target we can secure vs opponent,
    # with a small bonus for denying near-term captures.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place

        my_pos_d = 10**9
        my_op_d = -10**9
        my_best = None
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # secure score: if we can arrive <= opponent, prioritize; otherwise deny.
            if myd < opd:
                key_val = (0, myd, opd)  # lower is better
            elif myd == opd:
                key_val = (1, 0, 0)  # contested: slightly prefer smaller myd
            else:
                key_val = (2, -(opd - myd), myd)  # deny: maximize opponent lag, then my distance
            if my_best is None or key_val < my_pos_d:
                my_pos_d = key_val
                my_op_d = opd
                my_best = (rx, ry)

        # If we go somewhere, approximate opponent "who will take" our chosen best target.
        rx, ry = my_best
        myd = dist(nx, ny, rx, ry)
        opd = dist(ox, oy, rx, ry)

        # Denial bonus: if opponent can take some other resource in 1-2 moves after us,
        # prefer moves that increase the closest opponent target distance.
        opp_closest = 10**9
        for r2x, r2y in resources:
            opp_closest = min(opp_closest, dist(ox, oy, r2x, r2y))

        # Main objective: maximize chance to secure (arrive earlier), else maximize denial (opp lag)
        # plus a small tie-break favoring overall resource progress from our move.
        if myd < opd:
            val = (100 - myd) + (opd - myd) * 0.5 + (opp_closest) * 0.01
        elif myd == opd:
            val = 70 - myd + 0.2 * (opd - myd) + (opp_closest) * 0.01
        else:
            val = 40 + (opd - myd) * 1.2 + (opp_closest) * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]