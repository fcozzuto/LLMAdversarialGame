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

    # Prefer resources we can "race" to first (myd <= opd); if none, race the closest.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        win = 0 if myd <= opd else 1
        # Lower is better: win first, then maximize lead (opd-myd), then smaller myd.
        key = (win, myd - opd, myd, -opd, (rx * 37 + ry) % 1009)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        win = 0 if myd2 <= opd2 else 1
        # Also gently prefer moves that reduce our distance; tie-break deterministically.
        key = (win, myd2 - opd2, myd2, opd2, (dx * 7 + dy * 13) % 1009)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = [dx, dy]
    return [int(best_m[0]), int(best_m[1])]