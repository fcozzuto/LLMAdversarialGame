def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cur = (sx, sy)
    opp = (ox, oy)

    if not resources:
        best = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = md((nx, ny), opp)
            key = (d, dx == 0 and dy == 0, dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Choose a resource we can reach before the opponent (if any), else best swing.
    best_r_key = None
    best_r = resources[0]
    for r in resources:
        rd = (r[0], r[1])
        our_d = md(cur, rd)
        opp_d = md(opp, rd)
        gap = opp_d - our_d  # positive means we are closer
        reachable = 1 if our_d <= opp_d else 0
        key = (-reachable, -gap, our_d, rd[0], rd[1])
        if best_r_key is None or key < best_r_key:
            best_r_key = key
            best_r = rd

    tx, ty = best_r
    # Move one step: greedily reduce distance to target, while preserving advantage vs opponent.
    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        our_d = md((nx, ny), (tx, ty))
        opp_d = md(opp, (tx, ty))
        gap = opp_d - our_d
        # Penalize stalling and discourage moving to a step that makes us worse.
        stall_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (-gap, our_d, stall_pen, (nx - tx) ** 2 + (ny - ty) ** 2, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]