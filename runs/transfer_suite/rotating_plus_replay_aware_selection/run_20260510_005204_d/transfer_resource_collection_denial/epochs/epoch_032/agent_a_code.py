def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource that I can reach sooner than opponent, otherwise the least-losing one.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where I have an advantage; if tied, prefer closer and more "central".
        center = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (opd - myd, -myd, -opd, center)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = [0, 0]
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Scoring: increase advantage; also directly reward stepping onto any resource.
        step_gain = 0
        if any(rx == nx and ry == ny for rx, ry in resources):
            step_gain = 1000
        # Denial effect: if opponent is also close, prioritize lines that keep advantage positive.
        adv = (opd2 - myd2)
        sc = (100 * adv) - (myd2) + (5 * step_gain)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]
    return [int(best_mv[0]), int(best_mv[1])]