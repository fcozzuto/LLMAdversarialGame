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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # If on a resource, take it by staying.
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # Compute "race" advantage to each resource; deterministic tie-break.
    # Prefer immediate capture lanes: same-row or same-col slightly boosted.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd)  # positive means I'm closer in Chebyshev
        lane_bonus = 0
        if ry == sy or rx == sx:
            lane_bonus = 0.15
        # Also mildly prefer nearer resources to reduce delay.
        key = (round((adv + lane_bonus) * 1000), -myd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # If opponent is substantially closer to chosen target, counter by selecting
    # a resource that maximizes advantage among those not blocked from our move.
    # (This changes strategy when "sweep_rows" would otherwise steal.)
    chosen_myd = cheb(sx, sy, tx, ty)
    chosen_opd = cheb(ox, oy, tx, ty)
    if chosen_opd - chosen_myd >= 2:
        best2 = best
        best2_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            key = (adv, -myd, rx, ry)
            if best2_key is None or key > best2_key:
                best2_key = key
                best2 = (rx, ry)
        tx, ty = best2

    # Step toward target (diagonal allowed). Try to avoid immediate invalid moves.
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    prefs = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for ddx, ddy in prefs:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny):
            return [ddx, ddy]
    return [0, 0]