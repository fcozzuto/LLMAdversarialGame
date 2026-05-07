def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacles = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    resset = {(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2}

    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not resset:
        return [0, 0]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opppos = (ox, oy)

    # Target selection: prioritize resources where we are (or will be) ahead.
    best_r = None
    best_score = None
    for r in resset:
        dm = mdist(mypos, r)
        do = mdist(opppos, r)
        # score: margin in our favor, then closer to remove.
        sc = (do - dm, -dm, -r[0], -r[1])
        if best_score is None or sc > best_score:
            best_score = sc
            best_r = r

    tr = best_r
    base_my = mdist(mypos, tr)
    base_op = mdist(opppos, tr)

    # One-step lookahead: choose move that maximizes our advantage after moving.
    # Also include slight preference for reducing our distance to target.
    best_move = None
    best_mv_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = mdist((nx, ny), tr)
        opd = base_op  # opponent moves next, but we don't know; use our advantage only
        my_adv = (base_my - myd)  # positive if we get closer
        target_quality = myd
        sc = (my_adv, -target_quality, -dx, -dy)
        if best_mv_score is None or sc > best_mv_score:
            best_mv_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]