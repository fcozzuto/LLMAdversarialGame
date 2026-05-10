def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da if da > db else db

    # Select target resource: maximize "opponent disadvantage" (deterministic tie-break)
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive if we're closer
            key = (-adv, sd, od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer moves that reduce our distance to target; also prefer moves that worsen opponent relative distance.
        ds = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - ds

        # Micro-avoidance: penalize getting closer to nearest obstacle (no randomness; deterministic).
        if obstacles:
            mind = None
            for ax, ay in obstacles:
                d = cheb(nx, ny, ax, ay)
                if mind is None or d < mind:
                    mind = d
            obs_pen = 0 if mind is None else (10 - mind) if mind < 3 else 0
        else:
            obs_pen = 0

        # Pick lexicographically by (more advantage, closer to target, safer from obstacles, stable delta tie-break).
        score_key = (-adv, ds, obs_pen, nx, ny, dx, dy)
        if best_score is None or score_key < best_score:
            best_score = score_key
            best_move = [dx, dy]

    return best_move