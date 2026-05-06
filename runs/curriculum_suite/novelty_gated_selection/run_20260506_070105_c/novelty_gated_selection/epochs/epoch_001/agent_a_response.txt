def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # If no resources known, just stay.
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = None
        opp_best = None
        for r in resources:
            d_my = dist2((nx, ny), r)
            d_opp = dist2((ox, oy), r)
            if my_best is None or d_my < my_best:
                my_best = d_my
            if opp_best is None or d_opp < opp_best:
                opp_best = d_opp

        # Heuristic: get close, and prefer being closer than opponent on contested resources.
        # Also slightly penalize moving away from current best direction.
        my_cur = min(dist2((sx, sy), r) for r in resources)
        my_gain = my_cur - my_best  # positive is good
        val = 3.0 * my_gain - 1.0 * (my_best if my_best is not None else 0) + 0.35 * (opp_best - my_best)

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]