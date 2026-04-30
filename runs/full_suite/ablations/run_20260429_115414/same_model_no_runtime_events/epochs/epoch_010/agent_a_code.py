def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, bestv = 0, 0, -10**18

    opp_close = 0
    if res:
        opp_close = min(cheb(ox, oy, rx, ry) for rx, ry in res)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: prefer moving generally toward resources.
        v = -cheb(nx, ny, w - 1 - ox, h - 1 - oy) * 0  # deterministic no-op bias

        if res:
            # Evaluate best reachable target for us vs opponent.
            # Want targets where we are closer or can reach soon.
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < my_best: my_best = myd
                if opd < opp_best: opp_best = opd

            # Immediate steal potential: pick the best differential.
            best_diff = -10**9
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                diff = opd - myd  # positive if we are closer
                if diff > best_diff:
                    best_diff = diff

            v += 120 * best_diff
            v += 30 * (opp_close - cheb(nx, ny, ox, oy)) * 0  # no-op keep deterministic

            # Favor reducing our distance to the nearest resource.
            v += 25 * (-my_best)

            # Avoid walking into opponent's immediate race:
            # If opponent can reach a resource at most as fast as we can from next cell, discourage.
            if cheb(ox, oy, nx, ny) <= 2:
                v += -60

        # Obstacle-adjacent penalty to prevent bumping loops.
        # (Count blocked neighbors.)
        blocked_n = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if not ok(tx, ty):
                blocked_n += 1
        v += -3 * blocked_n

        # Small tie-break: keep closer to opponent slightly (deterministic pressure), but not dominant.
        v += -0.1 * cheb(nx, ny, ox, oy)

        if v > bestv or (v == bestv and (dx, dy) < (best_dx, best_dy)):
            bestv = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]