def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

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
        tx, ty = w - 1 - ox, h - 1 - oy
        best = (0, 0)
        bestv = 10**9
        for dxm in (-1, 0, 1):
            for dym in (-1, 0, 1):
                nx, ny = sx + dxm, sy + dym
                if not free(nx, ny):
                    nx, ny = sx, sy
                v = cheb(nx, ny, tx, ty)
                if v < bestv:
                    bestv = v
                    best = (dxm, dym)
        return [best[0], best[1]]

    best_t = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        closer = (opd - myd)  # positive if we arrive earlier
        # Prefer resources where we are earlier; if not, prefer those still relatively close to us
        # and slightly farther from opponent.
        score = closer * 1000 - myd * 3 + (opd - myd) * 10
        # Small deterministic bias to break ties
        score += (rx * 7 + ry * 11) * 1e-6
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    # Move toward target; if blocked, choose best alternative that still reduces distance.
    best = (0, 0)
    bestv = 10**9
    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, rx, ry)
            # Avoid stepping into positions that would likely give opponent the same resource advantage
            opd = cheb(ox + 0, oy + 0, rx, ry)
            myd_after = v
            tie_pen = (opd - myd_after) < 0  # if we're no longer earlier
            tv = v + (5 if tie_pen else 0)
            if tv < bestv:
                bestv = tv
                best = (dxm, dym)

    return [best[0], best[1]]