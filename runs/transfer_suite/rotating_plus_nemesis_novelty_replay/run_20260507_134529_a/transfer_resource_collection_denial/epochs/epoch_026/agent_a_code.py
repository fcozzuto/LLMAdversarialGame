def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))

    if not resources:
        return [0, 0]

    # Pick target: prefer resources where we already have a lead in Chebyshev distance.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        # If tie: prefer nearer for us, then farther for opponent (lower risk), then coordinate.
        key = (lead, -myd, -opd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Evaluate next move: go closer to target while denying opponent pickup next turn.
    # Assume pickup occurs when adjacent or on target (Chebyshev <= 1 after move resolution).
    opp_pick_now = cheb(ox, oy, tx, ty) <= 1
    best_m = (0, 0)
    best_v = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)

        # Bonus for immediate capture.
        v = 0
        if myd2 == 0:
            v += 10_000
        elif myd2 == 1:
            v += 500

        # Main gradient: minimize our distance, maximize opponent's distance.
        v += (1000 - 50 * myd2)
        v += (10 * opd2)

        # If opponent is close, strongly discourage moves that reduce their ability effectively.
        # Since we can't move opponent, we instead prioritize blocking by being the fastest to target.
        if opp_pick_now:
            v += 300 * (opd2 > 1)  # prefer states where opponent isn't effectively able
            v += 200 * (myd2 <= 1)

        # Mild tie-break by avoiding moving into crowded obstacle-nearby cells.
        near_obs = 0
        for adx, ady in moves:
            xx, yy = nx + adx, ny + ady
            if (xx, yy) in obstacles:
                near_obs += 1
        v -= 2 * near_obs

        key = (v, -myd2, -opd2, -nx, -ny)
        if best_v is None or key > best_v:
            best_v = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]