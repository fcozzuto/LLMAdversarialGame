def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    # Pick a target where we are much closer than opponent (Chebyshev).
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If aligned with opponent, bias against giving them an easy line.
        extra = 0
        if ry == oy:
            extra = (abs(ox - rx) - abs(sx - rx))
        key = (do - ds, extra, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that improve our lead to the chosen target,
        # and secondarily reduce opponent's lead and our distance to other resources.
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        lead = do2 - ds2
        # Small tie-break: head toward any collectible nearby.
        near = 999
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < near:
                near = d
        # Penalize stepping away from the target.
        back = cheb(nx, ny, tx, ty) - cheb(sx, sy, tx, ty)
        key = (lead, -ds2, -near, -abs(ry if False else 0), -back)
        if bestk is None or key > bestk:
            bestk = key
            bestm = [dx, dy]

    return bestm