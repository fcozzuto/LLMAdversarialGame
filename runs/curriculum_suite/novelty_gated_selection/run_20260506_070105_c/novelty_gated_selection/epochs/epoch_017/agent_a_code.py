def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    # Choose a target: prioritize resources where we are not already behind too much, but can catch.
    best_target = resources[0]
    best_tkey = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer targets we can reach sooner or roughly compete for.
        tkey = (opd - myd, myd, rx, ry)
        if best_tkey is None or tkey > best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    rx, ry = best_target

    # Diagonal probe tends to move along diagonals; try to counter by aligning with target direction.
    step_to_target = (0 if rx == sx else (1 if rx > sx else -1), 0 if ry == sy else (1 if ry > sy else -1))
    # Also compute a lightweight "intercept" step for opponent moving toward same target.
    opp_step = (0 if rx == ox else (1 if rx > ox else -1), 0 if ry == oy else (1 if ry > oy else -1))
    intercept_pos = (ox + opp_step[0], oy + opp_step[1])

    cur_my = man(sx, sy, rx, ry)
    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        myd = man(nx, ny, rx, ry)
        opd = man(ox, oy, rx, ry)

        score = 0
        # Main: win the race to target.
        score += (opd - myd) * 5

        # Strong preference to actually move toward target; punish regress.
        score += (cur_my - myd) * 2

        # Directional alignment: encourage steps consistent with diagonal probe countering.
        score += 0.6 * (dx * step_to_target[0] + dy * step_to_target[1])

        # Interference: if moving to/near likely opponent next cell toward target, prefer it.
        if inb(intercept_pos[0], intercept_pos[1]) and (nx, ny) == intercept_pos:
            score += 3.0

        # Avoid dead zones near obstacles by slight penalty if adjacent to obstacles (more robust).
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                px, py = nx + adx, ny + ady
                if (px, py) in obstacles:
                    adj_obs += 1
        score -= adj_obs * 0.25

        # Deterministic tie-breaker: prefer non-stay unless equally good, then smaller (dx,dy) lex.
        stay_pen = -0.01 if (dx, dy) != (0, 0) else 0.0
        score += stay_pen

        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1] and best[0] is not None:
            if (dx, dy) < best[0]:
                best = ((dx, dy), score)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    if not isinstance(dx, int) or not isinstance(dy, int):
        dx, dy = 0, 0
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        dx, dy = 0, 0
    return [dx, dy]