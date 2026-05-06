def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Predict opponent's nearest resource (tie by deterministic order).
    opp_target = None
    opp_best = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best:
            opp_best = d
            opp_target = (rx, ry)

    # Score resources by time advantage over opponent; bias against predicted target if we can't beat it.
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Higher is better: we want to be faster; also prefer farther from opponent when we can't win.
        s = (opd - myd) * 1000 + (opd + 1) - (myd + 1)
        if opp_target == (rx, ry) and myd >= opd:
            s -= 500  # discourage piling into their likely claim unless we can beat them
        if s > best_score:
            best_score = s
            best_r = (rx, ry)

    tx, ty = best_r
    # Choose the move that maximizes the eventual advantage improvement for the chosen resource;
    # include a small secondary objective to increase distance from obstacle-adjacent stagnation.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = (opd - myd2) * 1000 - myd2
        # Secondary: if opponent target exists, add pressure by moving toward it when we can still win that race.
        if opp_target is not None:
            r2x, r2y = opp_target
            myd3 = cheb(nx, ny, r2x, r2y)
            opd3 = cheb(ox, oy, r2x, r2y)
            if myd3 < opd3:
                val += 200
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]