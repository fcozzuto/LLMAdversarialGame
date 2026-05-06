def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Select a primary target deterministically: maximize "grab advantage" potential.
    # Grab advantage is (opp_dist - my_dist) after moving one step toward resource.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_my_min = min(man(sx, sy, rx, ry) for rx, ry in resources)
    cur_opp_min = min(man(ox, oy, rx, ry) for rx, ry in resources)

    # Precompute best target using current positions.
    best_t = resources[0]
    best_t_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources closer to us and further from opponent; tie-break by nearer overall.
        key = (-(opd - myd), myd + opd, rx, ry)
        if best_t_key is None or key < best_t_key:
            best_t_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Evaluate moves: (1) maximize advantage on target, (2) block opponent's approach to that target,
    # (3) reduce distance to target, (4) avoid moves that move away from global nearest resource.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        myd_t = man(nx, ny, tx, ty)
        opd_t = man(ox, oy, tx, ty)
        advantage = opd_t - myd_t

        # "Interference": if opponent is closer than us to the target, try to reduce opponent's ability
        # to get to the target quickly by moving toward a midpoint along our best path (deterministic proxy).
        # Midpoint proxy is one step toward target from us, but evaluated w.r.t. opponent distance.
        mx = sx + (1 if tx > sx else (-1 if tx < sx else 0))
        my = sy + (1 if ty > sy else (-1 if ty < sy else 0))
        mid_block = -man(ox, oy, mx, my)

        # Global progress: keep moving to overall nearest resource when target doesn't improve.
        myd_global = min(man(nx, ny, rx, ry) for rx, ry in resources)
        global_progress = cur_my_min - myd_global  # positive is good

        # Small penalty for increasing both my and global distances (prevents dithering).
        cur_global = cur_my_min
        away_pen = (myd_t - man(sx, sy, tx, ty)) + (myd_global - cur_global)

        val = advantage * 8 + (-myd_t) * 2 + global_progress * 1.5 + mid_block * 0.5 - away_pen * 0.75

        # If target is already adjacent and advantage is positive, staying is allowed but choose best anyway.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]