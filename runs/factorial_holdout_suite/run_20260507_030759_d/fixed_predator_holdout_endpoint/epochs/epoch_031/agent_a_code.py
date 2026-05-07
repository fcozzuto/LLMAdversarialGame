def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not in_bounds(x, y)
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_v = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            v = -md(nx, ny, tx, ty)
            if v > best_v:
                best_v = v
                best = [dx, dy]
        return best

    # Target selection: pick resource where we have the biggest approach advantage over opponent,
    # with a mild penalty for being too far away.
    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd == 0:
            val = 10**9
        else:
            val = (od - sd) * 100.0 - sd * 0.5
        # tie-breaker: deterministic on coordinates
        if best_res is None or val > best_val or (val == best_val and (rx, ry) < best_res):
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res

    # Local move choice: maximize progress to target while not stepping into obvious traps,
    # and slightly favor moves that improve our access to the second-best resource.
    res_list = sorted(resources, key=lambda r: (md(sx, sy, r[0], r[1]) + md(ox, oy, r[0], r[1]) * 0))
    # Second-best by same advantage metric
    second = None
    second_val = -10**18
    for rx, ry in resources:
        if (rx, ry) == (tx, ty): 
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        val = (od - sd) * 100.0 - sd * 0.5
        if second is None or val > second_val or (val == second_val and (rx, ry) < second):
            second_val = val
            second = (rx, ry)
    if second is None:
        second = (tx, ty)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d1 = md(nx, ny, tx, ty)
        d2 = md(nx, ny, second[0], second[1])
        # Avoid moves that make us closer to opponent than to target advantage-wise
        opp_d_to_n = md(nx, ny, ox, oy)
        target_progress = -d1
        second_progress = -0.25 * d2
        safety = 0.1 * (opp_d_to_n)  # prefer not moving adjacent to denier when indifferent
        # Small preference for staying if already best
        stay_bias = 0.02 if (dx == 0 and dy == 0) else 0.0
        score = target_progress + second_progress + safety + stay_bias
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move