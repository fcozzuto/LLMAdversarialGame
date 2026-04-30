def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick opponent-leaning target: resource with minimal opponent distance (tie: ours closer).
    best_t = None
    best_v = 10**9
    best_myd = 10**9
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs:
            continue
        od = cheb(ox, oy, rx, ry)
        md = cheb(sx, sy, rx, ry)
        if od < best_v or (od == best_v and md < best_myd):
            best_v, best_myd, best_t = od, md, (rx, ry)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # If we are on a resource, stay (or it would be useless to leave).
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # Evaluate moves: prioritize winning the target, then improve overall closeness, avoid self-traps near obstacles.
    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        target_win = opd - myd  # positive => we are closer than opponent
        # Secondary: be close to the nearest resource (overall).
        nearest = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in obs:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
        # Obstacle pressure: prefer moves with more free neighboring cells.
        free_nb = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay):
                free_nb += 1
        # Deterministic tie-break by move ordering already in deltas.
        score = target_win * 1000 - nearest + free_nb * 0.5
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]