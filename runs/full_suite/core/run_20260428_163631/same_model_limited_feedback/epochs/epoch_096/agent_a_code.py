def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    my_name = observation.get("self_name", "agent_a")
    _ = my_name  # unused, deterministic

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        dx = 0
        dy = 0
        best = (10**9, -10**9)
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_opp = dist2((nx, ny), (ox, oy))
            if (d_opp, -(ddx * 10 + ddy)) > best:
                best = (d_opp, -(ddx * 10 + ddy))
                dx, dy = ddx, ddy
        return [dx, dy]

    # Choose a resource to race for: prefer ones I'm closer to, and that the opponent isn't likely to take.
    best_target = None
    best_val = 10**18
    # Deterministic tie-breaker: lowest (val, x, y)
    for rx, ry in resources:
        myd = dist2((sx, sy), (rx, ry))
        opd = dist2((ox, oy), (rx, ry))
        # If opponent is much closer, penalize this resource.
        val = myd - 0.45 * opd
        if (val, rx, ry) < (best_val, (best_target[0] if best_target else 10**9), (best_target[1] if best_target else 10**9)):
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = (10**18, -10**18, 0, 0)
    # Best tuple: (distance_to_target, -distance_to_opponent, tie_breaker)
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = dist2((nx, ny), (tx, ty))
        d_o = dist2((nx, ny), (ox, oy))
        tie = (ddx + 1) * 3 + (ddy + 1)  # deterministic
        cand = (d_t, -d_o, tie, 0)
        if cand[:2] < best_move[:2] or (cand[:2] == best_move[:2] and tie < best_move[2]):
            best_move = (d_t, -d_o, tie, ddx + 10 * ddy)
            best_dx, best_dy = ddx, ddy

    return [int(best_dx), int(best_dy)]