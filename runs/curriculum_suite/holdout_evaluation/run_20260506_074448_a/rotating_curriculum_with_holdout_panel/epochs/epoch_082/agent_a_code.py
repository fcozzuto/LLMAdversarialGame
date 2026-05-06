def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by): 
        return abs(ax - bx) + abs(ay - by)
    def clamp_step(v, t): 
        return 0 if v == t else (1 if t > v else -1)

    if not resources:
        return [0, 0]

    # Opponent's likely target: their nearest available resource (deterministic).
    best_o = None; best_ko = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        d = man(ox, oy, rx, ry)
        ko = (d, rx, ry)
        if best_ko is None or ko < best_ko:
            best_ko = ko; best_o = (rx, ry)

    # If we share/contest the target, we go into "interceptor" mode by reducing
    # distance to the opponent's target more aggressively than just pursuing our own.
    tx, ty = best_o
    myd = man(sx, sy, tx, ty)
    oppd = man(ox, oy, tx, ty)
    # Interception threshold tuned to be robust: only fall back if we are clearly worse.
    if oppd - myd <= 1:
        dx = clamp_step(sx, tx); dy = clamp_step(sy, ty)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            # Try a perpendicular step to skirt obstacles deterministically.
            cand = [(dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]
            for ddx, ddy in cand:
                if (sx + ddx, sy + ddy) not in obstacles:
                    return [ddx, ddy]
            return [0, 0]
        return [dx, dy]

    # Otherwise, opportunistically pick a resource where we have tempo advantage,
    # but also bias to keep moving along the diagonal toward the center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_t = None; best_k = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my = man(sx, sy, rx, ry); op = man(ox, oy, rx, ry)
        tempo = op - my  # prefer positive tempo
        cent = abs(cx - rx) + abs(cy - ry)
        # Prefer "frontier" resources if tempo is similar.
        key = (-tempo, cent, my, rx, ry)
        if best_k is None or key < best_k:
            best_k = key; best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    rx, ry = best_t
    dx = clamp_step(sx, rx); dy = clamp_step(sy, ry)
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministic obstacle-avoidance: try axis steps first, then stay.
        cand = [(dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy), (-dx, -dy)]
        for ddx, ddy in cand:
            if (sx + ddx, sy + ddy) not in obstacles:
                return [ddx, ddy]
        return [0, 0]
    return [dx, dy]