def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose a target resource based on current "pressure" from opponent
    best_r = None
    best_val = -10**18
    for r in resources:
        r = (r[0], r[1])
        if r in obstacles:
            continue
        myd = dist2((sx, sy), r)
        opd = dist2((ox, oy), r)
        # Prefer resources we are closer to; if tied, prefer those farther from opponent.
        val = (opd - myd) - 0.01 * myd
        if val > best_val:
            best_val = val
            best_r = r
    if best_r is None:
        best_r = (resources[0][0], resources[0][1])

    tx, ty = best_r

    # Candidate move evaluation
    cand_best = -10**18
    cand_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # If we can grab the target immediately, be decisive
        my_to_target = dist2((nx, ny), (tx, ty))
        # Compute how close we are to any resource; helps avoid getting stuck
        min_res = 10**18
        pressure_penalty = 0.0
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            d_self = dist2((nx, ny), (rx, ry))
            d_opp = dist2((ox, oy), (rx, ry))
            if d_self < min_res:
                min_res = d_self
            # Penalize resources likely to be taken by opponent before we arrive
            if d_self > 0:
                my_gain = (d_opp - d_self)
                if my_gain < 0:
                    pressure_penalty += (-my_gain) / (1.0 + d_self)
        # Encourage separation from opponent to reduce contesting
        sep = dist2((nx, ny), (ox, oy))

        # Main objective: reach target quickly; otherwise, maximize advantage
        score = 0.0
        score += 1000000.0 if my_to_target == 0 else 0.0
        score += -2.5 * my_to_target
        score += -0.15 * min_res
        score += 0.02 * sep
        score -= 0.6 * pressure_penalty

        if score > cand_best:
            cand_best = score
            cand_move = [dx, dy]

    return cand_move