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

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; then maximize how much we are ahead.
        # If all are behind, choose the one where we lose by the smallest margin.
        margin = opd - myd
        key = (
            0 if margin >= 0 else 1,
            -margin if margin >= 0 else abs(margin),
            (rx * 17 + ry * 31) % 101,
            myd
        )
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)

        # Small deterministic pressure: move that also tends to increase opponent's distance from our target.
        opd2 = cheb(ox, oy, tx, ty)

        # If we can already collect (standing on target), prioritize it strongly.
        collect = 0 if (nx == tx and ny == ty) else 1

        # Mild bias to avoid obstacles isn't needed (invalid moves are filtered), but prefer center-ish deterministically.
        center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)

        key = (collect, myd2, -(opd2), center_bias, (dx + 2) * 7 + (dy + 2))
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]