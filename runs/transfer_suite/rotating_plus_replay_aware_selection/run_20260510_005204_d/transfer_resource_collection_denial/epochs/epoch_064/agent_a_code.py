def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target resource we are relatively closest to (deterministic).
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: we are closer than opponent; then closer to resource; then stable tie-breaker.
        key = (myd - opd, myd, -opd, (rx * 31 + ry) % 997)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Move to neighbor that best improves our relative advantage.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None

    # Small bias toward bottom-right if we are not yet taking advantage; helps break ties and deny.
    corner_bias_x = (w - 1) if sy % 2 == 0 else 0
    corner_bias_y = h - 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer reducing relative gap and my distance; secondarily reduce distance to a preferred corner.
        rel = myd2 - opd2
        corner_d = cheb(nx, ny, corner_bias_x, corner_bias_y)
        key = (rel, myd2, corner_d, -opd2, (dx + 2) * 7 + (dy + 2))
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]