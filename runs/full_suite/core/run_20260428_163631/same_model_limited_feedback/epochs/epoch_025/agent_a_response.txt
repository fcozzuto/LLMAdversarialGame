def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (ox, oy))
            sc = (-d, 0, -dx, -dy)
            if sc < (best[0], best[1], best[2], best[3]):
                best = (-d, 0, -dx, -dy)
        return [best[2] * -1, best[3] * -1] if (best[2] or best[3]) else [0, 0]

    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        # prioritize resources closer to self than opponent; also slight bias to nearer overall
        val = (dO - dS) * 10 - dS
        if (rx, ry) in obstacles:
            val -= 1000
        if val > best_val or (val == best_val and (rx, ry) < best_target):
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    best_score = -10**18
    best_move = (0, 0)
    # deterministic tie-break: prefer moves that reduce distance to target; then smaller dx, dy lexicographically
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_now = dist((nx, ny), (tx, ty))
        d_self = dist((sx, sy), (tx, ty))
        # predict opponent contest on the same target: assume opponent will move to minimize its distance
        dO_cur = dist((ox, oy), (tx, ty))
        opp_best = dO_cur
        for odx, ody in moves:
            pnx, pny = ox + odx, oy + ody
            if not in_bounds(pnx, pny) or (pnx, pny) in obstacles:
                continue
            opp_best = min(opp_best, dist((pnx, pny), (tx, ty)))
        # score: being closer is good; also winning the contest is big; penalize giving up too much
        score = (dO_cur - opp_best) * 8 + (d_self - d_now) * 6 - d_now
        if (nx, ny) == (tx, ty):
            score += 1000
        tie = (score == best_score and (dx, dy) < best_move)
        if score > best_score or tie:
            best_score = score
            best_move = (dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]