def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not res:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Build deterministic ordering for tie-breaking
    def res_key(r):
        return (r[0], r[1])

    resources = sorted([(r[0], r[1]) for r in res], key=res_key)

    best = (None, -10**9, 0, 0, 0)  # (move, score, adv, targetx, targety)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Consider each resource as a "race"; score is how much we can beat opponent by next step.
        # Prefer stealing resources we are not currently guaranteed to reach first, and avoid moves that
        # allow opponent a clear lead.
        local_best_margin = -10**9
        local_best_adv = -10**9
        local_target = resources[0]

        for rx, ry in resources:
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            margin = opp_d - self_d  # positive is better for us
            # Slightly prefer nearer targets among equal margin
            adv = margin * 1000 - self_d
            if adv > local_best_adv or (adv == local_best_adv and (margin > local_best_margin or (margin == local_best_margin and (rx, ry) < local_target))):
                local_best_adv = adv
                local_best_margin = margin
                local_target = (rx, ry)

        # Penalize staying put if it doesn't improve margin
        stay_pen = -20 if (dx == 0 and dy == 0) else 0

        # Also incorporate a "threat" term: count resources where opponent is already significantly closer
        threat = 0
        for rx, ry in resources:
            sd0 = abs(sx - rx) + abs(sy - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if od - sd0 >= 2:
                threat += 1

        # Score favors largest achievable margin, then reduces threat and step cost
        step_cost = abs(nx - local_target[0]) + abs(ny - local_target[1])
        score = local_best_margin * 100 - threat - step_cost + stay_pen

        if score > best[1] or (score == best[1] and (local_best_margin > best[2] or (local_best_margin == best[2] and (local_target < (best[3], best[4]))))):
            best = ((dx, dy), score, local_best_margin, local_target[0], local_target[1])

    return [best[0][0], best[0][1]]