def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]

    # Deterministic ordering of candidate resources
    res = [tuple(p) for p in resources]
    if not res:
        return [0, 0]
    res.sort(key=lambda r: (r[0] * 31 + r[1]) % 97)

    best = None
    best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer reachable resources that we can secure: minimize (myd - opponent advantage).
        # Higher opponent distance is better => subtract from key.
        # Add small deterministic bias to break ties.
        key = (myd - 0.65 * (opd - myd), myd, -opd, (rx * 31 + ry) % 101)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance to target; also prefer increasing our advantage.
        # If tied, prefer keeping closer to center slightly (stable behavior).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = abs(nx - cx) + abs(ny - cy)
        key = (myd2 - 0.7 * (opd2 - myd2), myd2, -opd2, center_bias, (dx + 2 * dy) % 7)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]