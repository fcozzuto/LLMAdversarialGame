def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    tr = observation.get("turns_remaining", 0) or 0

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, cheb(ox, oy, tx, ty))
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose resource where we have a stronger "can-capture-first" edge.
    best_key = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Capture-likelihood heuristic: prefer ds <= do, then larger margin, then smaller ds.
        # If time is short, strongly prefer immediate reachability.
        time_bias = 0
        if tr <= 8:
            time_bias = 10 if ds <= tr else -10
        cap_ok = 1 if ds <= do else 0
        key = (-cap_ok, -(do - ds), time_bias, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # If we can’t secure quickly, keep pressure by moving to reduce distance most.
        # Small tie-breaker: avoid moving closer to opponent if both compete equally.
        opp_threat = cheb(ox, oy, tx, ty) - cheb(ox, oy, tx, ty)
        k = (d, opp_threat, abs((nx - tx)) + abs((ny - ty)), dx, dy)
        if best is None or k < best[0]:
            best = (k, [dx, dy])
    return best[1] if best else [0, 0]