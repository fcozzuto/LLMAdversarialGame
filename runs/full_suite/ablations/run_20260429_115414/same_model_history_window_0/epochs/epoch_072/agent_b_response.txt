def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    my = observation["self_position"]
    op = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def inb(p):
        return 0 <= p[0] < w and 0 <= p[1] < h

    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)

    # Choose a target resource where we are relatively advantaged over the opponent
    best_t = resources[0]
    best_m = None
    for r in resources:
        myd = dist(my, r)
        opd = dist(op, r)
        m = myd - 0.6 * opd  # prefer resources closer than opponent
        if best_m is None or m < best_m or (m == best_m and r[0] < best_t[0]):
            best_m = m
            best_t = r

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    best_opp = None

    for dx, dy in deltas:
        np = (my[0] + dx, my[1] + dy)
        if not inb(np):
            continue
        if np in obstacles:
            continue
        myd = dist(np, best_t)
        opd = dist(op, best_t)
        oppdist_me = dist(np, op)
        val = myd - 0.25 * opd  # move closer to target while keeping pressure
        # tie-breakers: maximize distance from opponent, then deterministic order
        if best_val is None or val < best_val or (val == best_val and oppdist_me > best_opp) or \
           (val == best_val and oppdist_me == best_opp and (dx, dy) < best_move):
            best_val = val
            best_opp = oppdist_me
            best_move = (dx, dy)

    # If all moves blocked by obstacles, allow one that doesn't increase distance too much
    if best_val is None:
        for dx, dy in deltas:
            np = (my[0] + dx, my[1] + dy)
            if not inb(np):
                continue
            myd = dist(np, best_t)
            oppdist_me = dist(np, op)
            val = myd + (0.1 if np in obstacles else 0.0)
            if best_val is None or val < best_val or (val == best_val and oppdist_me > best_opp) or \
               (val == best_val and oppdist_me == best_opp and (dx, dy) < best_move):
                best_val = val
                best_opp = oppdist_me
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]