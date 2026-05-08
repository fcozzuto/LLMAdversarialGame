def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources we can arrive earlier or at same time; then maximize advantage; then closest.
        # Tie-break: deterministic preference by coordinates.
        key = (myd > opd, opd - myd, -myd, -(rx * 97 + ry * 53))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # Choose move that decreases our distance to target and keeps/opens lead vs opponent.
        key = (myd2 > opd2, (opd2 - myd2) * -1, myd2, dx * 7 + dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]