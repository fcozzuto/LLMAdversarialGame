def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, dx, dy) < best:
                best = (d, dx, dy)
        return [best[1], best[2]]

    res = [tuple(p) for p in resources]
    res_set = set(res)
    ox, oy = observation["opponent_position"]

    best_r = None
    best_score = -10**30
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise nearest.
        if ds < do:
            sc = (do - ds) * 1000 - ds
        else:
            sc = -ds - (ds == do) * 0.1
        if sc > best_score:
            best_score = sc
            best_r = (rx, ry)
        elif sc == best_score:
            # Deterministic tie-break
            if best_r is None or (rx, ry) < best_r:
                best_r = (rx, ry)

    tx, ty = best_r
    best = (10**9, -10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in res_set:
            # Immediate pickup dominates
            return [dx, dy]
        d_to_target = cheb(nx, ny, tx, ty)
        # Slightly prefer moves that also reduce opponent's distance to this target (deny race)
        do_next = cheb(ox, oy, tx, ty)
        sc_deny = 0.0
        if do_next <= d_to_target:
            sc_deny = -0.01 * d_to_target
        key = (d_to_target, -sc_deny, dx, dy)
        if key < best:
            best = key

    return [best[2], best[3]]