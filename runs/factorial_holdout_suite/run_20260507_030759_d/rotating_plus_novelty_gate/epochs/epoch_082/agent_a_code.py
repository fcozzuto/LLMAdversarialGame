def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    res = [tuple(p) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    def md(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in set(res):
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal or not res:
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    # Opponent "shadow" target: the resource they are closest to right now.
    best_do = None
    r_op = None
    for r in res:
        d = md(opp, r)
        if best_do is None or d < best_do or (d == best_do and r < r_op):
            best_do, r_op = d, r

    # If we can contest it (not worse than opponent), chase it; otherwise grab closest for ourselves.
    dm_op = md(my, r_op)
    if dm_op <= best_do:
        target = r_op
    else:
        best_dm = None
        target = None
        for r in res:
            d = md(my, r)
            if best_dm is None or d < best_dm or (d == best_dm and r < target):
                best_dm, target = d, r

    tx, ty = target
    # Choose move that minimizes distance to target with deterministic tie-break; slight bias to reduce opponent distance too.
    best = None
    best_mv = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = md((nx, ny), (tx, ty))
        d_opp = md(opp, (tx, ty))
        key = (d_self, -(d_opp - d_self), dx, dy)
        if best is None or key < best:
            best, best_mv = key, (dx, dy)
    return [best_mv[0], best_mv[1]]