def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    rem = observation.get("remaining_resource_count", len(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources or rem <= 0:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
    else:
        # Target resources where we are less behind than opponent (or we are ahead).
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # bigger is better
            # Encourage earlier approach to mid-board to reduce tie oscillation.
            mid_bias = -((abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)))
            # Small deterministic tie-break: prefer low x then low y.
            key = (lead, mid_bias, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    alpha = 1.3 if resources else 1.0
    beta = 0.15 if resources else 0.0

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance; if tied, prefer increasing opponent distance (indirect contest).
        s = (-myd2) + alpha * (-opd2) + beta * (dx == 0 and dy == 0)
        # Deterministic final tie-break to avoid jitter.
        t = (-abs(nx - tx) - abs(ny - ty), -nx, -ny, dx, dy)
        score = (s, t)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]