def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Time horizon: use turns_remaining to bias toward doable captures.
    tr = int(observation.get("turns_remaining", 0))
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by attempting to secure a resource we can reach no later than opponent.
        local_best_ahead = None
        local_best_fallback = None
        for rx, ry in resources:
            d_us = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            ahead = d_op - d_us  # positive => we are closer

            # Prefer resources we can realistically secure before/around horizon.
            # If tr is unknown/zero, this still provides slight bias.
            if tr > 0:
                if d_us > tr:
                    continue

            if local_best_ahead is None:
                local_best_ahead = (-ahead, d_us, rx, ry) if ahead <= 0 else (-1, -ahead, d_us, rx, ry)
            # We'll compute actual comparison consistently below:
            if ahead > 0:
                cand = (0, -ahead, d_us, rx, ry)  # best: highest ahead
            else:
                cand = (1, d_us, d_op, rx, ry)   # fallback: closest we can get
            if local_best_fallback is None:
                local_best_fallback = cand
            else:
                local_best_fallback = min(local_best_fallback, cand)

        # If horizon filtering eliminated all, use pure heuristic.
        if local_best_fallback is None:
            for rx, ry in resources:
                d_us = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                ahead = d_op - d_us
                cand = (0, -ahead, d_us, rx, ry) if ahead > 0 else (1, d_us, d_op, rx, ry)
                local_best_fallback = cand if local_best_fallback is None else min(local_best_fallback, cand)

        # Add small deterrent against moves that let opponent get adjacent to us (reduce chance of interference).
        opp_adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        val = (local_best_fallback, 1 if opp_adj else 0)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]