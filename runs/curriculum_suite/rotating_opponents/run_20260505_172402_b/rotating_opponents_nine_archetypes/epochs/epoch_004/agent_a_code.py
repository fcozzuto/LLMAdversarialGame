def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs_set

    def step_towards(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        return px + dx, py + dy

    def man(a, b, c, d):
        return abs(c - a) + abs(d - b)

    best_target = None
    best_score = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources I'm meaningfully closer to than opponent, plus safety if near opponent
        prox_opp = man(sx, sy, ox, oy)
        score = (opd - myd) * 3 - myd
        if prox_opp <= 2:
            score -= (3 - prox_opp) * 4  # avoid being too eager when opponent is adjacent
        if best_score is None or score > best_score or (score == best_score and myd < best_target[0]):
            best_score = score
            best_target = (myd, rx, ry)

    if not best_target:
        # No resources info; drift away from opponent while staying valid
        bestd, bestmv = None, (0, 0)
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            if bestd is None or d > bestd:
                bestd, bestmv = d, (ddx, ddy)
        return [bestmv[0], bestmv[1]]

    _, rx, ry = best_target
    tx, ty = step_towards(sx, sy, rx, ry)
    if valid(tx, ty):
        dx, dy = tx - sx, ty - sy
        return [dx, dy]

    # Fallback: choose any valid move minimizing distance to chosen target, with tie-break to keep away from opponent
    cur_best = None
    cur_mv = (0, 0)
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        d1 = man(nx, ny, rx, ry)
        d2 = man(nx, ny, ox, oy)
        cand = (d1, -d2, abs(ddx) + abs(ddy))
        if cur_best is None or cand < cur_best:
            cur_best, cur_mv = cand, (ddx, ddy)
    return [cur_mv[0], cur_mv[1]]