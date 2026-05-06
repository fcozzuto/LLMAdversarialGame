def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # "Intercept/deny": prefer moves that make us closer to the resources than the opponent,
    # and otherwise move to reduce the gap while heading toward the action region.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd_to_best = 10**9
        opd_to_best = 10**9
        myd_minus_opd = 10**9
        nearest_res = 10**9
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gap = myd - opd  # negative => we are closer (deny/contest)
            if gap < myd_minus_opd or (gap == myd_minus_opd and (myd < myd_to_best or (myd == myd_to_best and opd < opd_to_best))):
                myd_minus_opd = gap
                myd_to_best = myd
                opd_to_best = opd
            if myd < nearest_res:
                nearest_res = myd

        center_dist = abs(nx - cx) + abs(ny - cy)

        # Lexicographic minimization: best denial first, then own progress, then reduce opponent progress,
        # then center pressure for future interception.
        key = (
            -(1 if myd_minus_opd <= 0 else 0),  # prioritize being at least as close as opponent
            myd_minus_opd,
            myd_to_best,
            -opd_to_best,
            nearest_res,
            center_dist,
            dx * 3 + dy  # deterministic tie-break
        )
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]