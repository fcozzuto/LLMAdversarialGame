def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    myx, myy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    res_set = {(p[0], p[1]) for p in resources}

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    def dist(a, b):
        ax, ay = a; bx, by = b
        d1 = abs(ax - bx)
        d2 = abs(ay - by)
        return d1 if d1 > d2 else d2  # Chebyshev for diagonal step metric

    # If resources exist, select move that best improves access vs opponent
    best = None
    best_score = -10**9
    center = (w // 2, h // 2)

    for dx, dy in moves:
        nx, ny = clamp(myx + dx, 0, w - 1), clamp(myy + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            continue
        # small penalty near obstacles to avoid traps
        near_obs = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if (nx + tx, ny + ty) in obs_set:
                    near_obs += 1
        my_d_to_best = 0
        opp_d_to_best = 0
        if resources:
            # choose best resource under my vs opponent distance advantage
            for rx, ry in resources:
                myd = dist((nx, ny), (rx, ry))
                oppd = dist((ox, oy), (rx, ry))
                # prefer picking/contesting resources; picking gets big bonus via myd==0
                advantage = (oppd - myd)
                score = 5.0 * advantage - 0.35 * myd + (10.0 if myd == 0 else 0.0)
                # if I'm moving toward a resource while opponent is already on top, still avoid losing it
                if oppd == 0 and myd != 0:
                    score -= 12.0
                score -= 0.05 * near_obs
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
                    my_d_to_best, opp_d_to_best = myd, oppd
        else:
            # no resources: drift toward center
            score = -dist((nx, ny), center) - 0.05 * near_obs
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        # Fallback: avoid obstacles, otherwise move toward center
        tx, ty = center
        cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in cand:
            nx, ny = clamp(myx + dx, 0, w - 1), clamp(myy + dy, 0, h - 1)
            if (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    return [int(best[0]), int(best[1])]