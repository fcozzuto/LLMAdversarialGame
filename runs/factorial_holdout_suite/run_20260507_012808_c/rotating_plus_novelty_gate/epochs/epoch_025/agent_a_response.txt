def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if w <= 0 or h <= 0:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    if not resources:
        # fallback: drift toward center-ish without collisions
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                v = -dist(nx, ny, tx, ty)
                if v > best_val:
                    best_val = v
                    best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource and move to maximize capture margin.
    # Capture margin = (opp_dist - my_dist) plus small advantage for being closer.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = -10**18
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer landing on the resource (myd==0), and when tied, prefer that we are closer than opponent.
            v = (opd - myd) * 10 - myd
            if myd == 0:
                v += 100
            my_best = v if v > my_best else my_best
        # Encourage safety: keep away from obstacles by penalizing being "stuck" (few valid moves)
        # Small deterministic bias toward increasing x then y to break ties.
        safety = 0
        k = 0
        for ddx, ddy in moves:
            tx2, ty2 = nx + ddx, ny + ddy
            if valid(tx2, ty2):
                k += 1
        safety = -5 if k <= 2 else 0
        tie = (dx == 0 and dy == 0) * (-1)
        vtot = my_best + safety + tie
        if vtot > best_val:
            best_val = vtot
            best = (dx, dy)

    # If somehow none were valid (rare), stay put.
    if best_val == -10**18:
        return [0, 0]
    return [best[0], best[1]]