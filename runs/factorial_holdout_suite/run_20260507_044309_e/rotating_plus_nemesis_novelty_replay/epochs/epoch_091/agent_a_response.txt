def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def blocked(x, y):
        return (x, y) in obstacles

    # Pick a resource that maximizes immediate advantage: (opp dist - self dist).
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        delta = do - ds
        key = (delta, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = None

    # Greedy step: improve your closeness to target, and also worsen opponent's closeness to that same target.
    # Add slight anti-collision to avoid moving into opponent if equally good.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)
        cur_do = cheb(ox, oy, rx, ry)
        adv = cur_do - nds  # desired bigger
        # Evaluate also a potential chase of the nearest alternative to prevent being cut off
        min_do_alt = ndo
        min_ds_alt = nds
        for arx, ary in resources:
            ds2 = cheb(nx, ny, arx, ary)
            do2 = cheb(ox, oy, arx, ary)
            if ds2 < min_ds_alt:
                min_ds_alt = ds2
            if do2 < min_do_alt:
                min_do_alt = do2
        opp_pressure = (cur_do - min_do_alt)  # smaller is better for us; but keep sign consistent
        opp_pressure = -opp_pressure

        dist_to_opp = cheb(nx, ny, ox, oy)
        score_tuple = (adv, -nds, opp_pressure, dist_to_opp, -dx, -dy)
        if best_score is None or score_tuple > best_score:
            best_score = score_tuple
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]