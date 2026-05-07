def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    res_set = set(tuple(r) for r in resources)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    if not resources:
        # Drift to nearest border away from opponent sweep patterns: move to side opposite opponent x
        target_x = 0 if ox > (w - 1) / 2 else (w - 1)
        best = None; bestv = None
        for dx, dy, nx, ny in valid:
            v = cheb(nx, ny, target_x, sy) - (0 if ox == nx else 0)
            if bestv is None or v < bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best = None
    best_score = None
    # Prefer resources I can arrive at earlier; otherwise choose the one with minimal delay,
    # and slightly prefer resources on/near opponent's current row to enable interception.
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        time_adv = do - dme  # positive => I reach sooner
        intercept = 0
        if ry == oy:
            intercept = 1.0
        else:
            intercept = -0.25 * cheb(ox, oy, rx, ry)
        # Add slight preference to closer targets to keep determinism robust
        closeness = -0.05 * dme
        score = (2.0 * time_adv) + intercept + closeness
        if best_score is None or score > best_score or (score == best_score and dme < cheb(sx, sy, best[0], best[1])):
            best_score = score
            best = (rx, ry)

    tx, ty = best
    # Choose move that reduces distance to target; if tie, reduce opponent distance too.
    best_move = None
    best_tuple = None
    for dx, dy, nx, ny in valid:
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer becoming closer to target; tie-breaker: make opponent also farther in time sense
        tieb = (od - cheb(ox, oy, tx, ty))  # always 0, but keep structure deterministic
        tup = (myd, - (od - myd), tieb)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]