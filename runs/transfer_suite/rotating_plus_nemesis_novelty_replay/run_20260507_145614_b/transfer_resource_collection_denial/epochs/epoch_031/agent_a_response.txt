def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic ordering for ties
    best_move = (0, 0)
    best_val = -10**18

    # If no resources, go to center-ish
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Precompute opponent's nearest resource distance for "race" bias
    opp_nearest = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        myd_step_to_best = 10**9
        opd_step_to_that = 0
        race_adv_best = -10**9

        # Choose the most winnable resource relative to opponent
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race_adv = opd - myd  # positive means we close faster
            if race_adv > race_adv_best or (race_adv == race_adv_best and myd < myd_step_to_best):
                race_adv_best = race_adv
                myd_step_to_best = myd
                opd_step_to_that = opd

        # Heuristic:
        # - strong preference for being closer than opponent (race_adv)
        # - slight preference for shorter own distance
        # - if we're losing most races, steer toward reducing opponent-nearest gap
        if race_adv_best >= 0:
            val = 1200 * race_adv_best - 10 * myd_step_to_best
        else:
            # We're behind: try to at least approach a resource where opponent is relatively near,
            # to prevent them from taking it uncontested.
            val = 200 * race_adv_best - 5 * myd_step_to_best - 2 * (opd_step_to_that - opp_nearest)
        # Prefer fewer steps near obstacles naturally via valid() only; deterministic tie-break:
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]