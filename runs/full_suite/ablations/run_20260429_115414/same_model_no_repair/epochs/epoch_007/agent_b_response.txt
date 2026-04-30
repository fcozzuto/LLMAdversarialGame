def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Pick the resource where we have the biggest distance advantage over opponent.
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            adv = opd - myd
            key = (adv, -myd, -rx, -ry)  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Score each legal move by improvement toward target, while keeping distance from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = abs(tx - nx) + abs(ty - ny)
        opd = abs(tx - ox) + abs(ty - oy)

        # Encourage taking target: smaller myd, larger advantage (opponent further).
        # Penalize giving opponent a nearer path to the target on next step.
        myd_now = abs(tx - sx) + abs(ty - sy)
        my_improve = myd_now - myd

        # Also lightly avoid getting too close to opponent unless we're close to target.
        close_pen = 0
        if opponent_near := (abs(nx - ox) + abs(ny - oy) <= 2):
            close_pen = -0.3 * (2 - (abs(nx - ox) + abs(ny - oy)))

        score = (my_improve * 2.0) + (opd - myd) + close_pen - 0.05 * myd
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]