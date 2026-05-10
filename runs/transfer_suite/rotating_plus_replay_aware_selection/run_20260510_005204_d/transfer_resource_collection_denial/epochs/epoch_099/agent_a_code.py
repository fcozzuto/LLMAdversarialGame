def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not resources:
        return [0, 0]

    if any(r[0] == sx and r[1] == sy for r in resources):
        return [0, 0]

    late = 1.0 if turns_remaining <= 10 else 0.0
    focus_my_pick = 0.35 + 0.65 * late
    focus_race = 1.0 - focus_my_pick

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_val = -10**18
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate urgency to own nearest resource
        my_best = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_best:
                my_best = d

        # Race advantage: prefer resources where we are closer than opponent
        val = -focus_my_pick * my_best
        min_opp = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd < min_opp:
                min_opp = opd
            # Large weight to stealing resources from opponent
            val += focus_race * (opd - myd) * 8.0
            # Small tie-break favoring reachable earlier
            val += -0.6 * myd
            # Slightly prefer staying away from opponent unless late game
            if not late:
                val += 0.2 * cheb(nx, ny, ox, oy)

        # Avoid stepping into opponent's likely sweep line (same row/col) early
        if not late:
            if (ny == oy or nx == ox):
                val -= 3.0
            if (ny == oy and ox != sx) or (nx == ox and oy != sy):
                val -= 1.0

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]