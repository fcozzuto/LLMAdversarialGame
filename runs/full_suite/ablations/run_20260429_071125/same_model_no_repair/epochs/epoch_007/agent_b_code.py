def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            v = -((nx - cx) ** 2 + (ny - cy) ** 2) - 0.1 * man(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource: prioritize ones we can reach no slower than opponent; else the most favorable race.
    best_target = None
    best_key = None  # higher is better
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = opd - myd  # positive if we are faster
        # Deterministic tie-break: prefer closer, then higher lead.
        key = (lead, -myd, -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    want_dx, want_dy = step_towards(tx, ty)

    # Evaluate all legal moves with a local heuristic toward the chosen target and avoiding obstacles.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        nd = man(nx, ny, tx, ty)
        # discourage stepping away from desired direction
        dir_pen = (want_dx != 0 and dx != want_dx) or (want_dy != 0 and dy != want_dy)
        # small race term: prefer states that worsen opponent distance to target
        opd = man(ox, oy, tx, ty)
        my_future = nd
        race = (opd - my_future)
        # discourage proximity to obstacles (soft)
        close_obs = 0
        for ax, ay in obstacles:
            d = abs(nx - ax) + abs(ny - ay)
            if d == 1:
                close_obs += 1
        v = (1000 * (race >= 0)) + race - 2 * nd - (1.5 if dir_pen else 0) - 0.3 * close_obs
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]