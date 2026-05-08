def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = -10**9
        for dxm in (-1, 0, 1):
            for dym in (-1, 0, 1):
                nx, ny = sx + dxm, sy + dym
                if not free(nx, ny):
                    nx, ny = sx, sy
                v = -(cheb(nx, ny, tx, ty))
                if v > bestv:
                    bestv = v
                    best = (dxm, dym)
        return [best[0], best[1]]

    # Target: resource where we can arrive earlier and/or likely secure before time runs out
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = ((opd - myd) * 120 + (turns_remaining - myd >= 0) * 40 - myd, -opd, -rx - 0.001 * ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    bestv = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            nx, ny = sx, sy
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Interception-style: maximize advantage, but also reduce opponent's potential relative gain
        advantage = opd2 - myd2
        progress = -myd2
        time_bonus = 10 if myd2 <= turns_remaining else -10
        obstacle_stay_pen = -3 if (nx, ny) == (sx, sy) and (dxm, dym) != (0, 0) else 0
        # Small deterministic tie-breaker
        tie = -abs(nx - tx) - 0.001 * abs(ny - ty)
        v = advantage * 100 + progress * 10 + time_bonus + obstacle_stay_pen + tie
        if v > bestv:
            bestv = v
            best_move = (dxm, dym)
    return [best_move[0], best_move[1]]