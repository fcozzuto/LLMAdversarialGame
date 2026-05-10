def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target resource: prioritize those we can reach strictly before opponent; otherwise minimize our distance.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        if myd < opd:
            key = (0, myd, opd, rx, ry)
        else:
            key = (1, opd - myd, myd, opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_sc = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources and (nx, ny) in resources:
            return [dx, dy]

        my_next = dist(nx, ny, tx, ty)
        op_now = dist(ox, oy, tx, ty)
        margin = op_now - my_next  # higher is better (we want to be at/under opponent reach)
        progress = dist(sx, sy, tx, ty) - my_next  # positive means closer

        # Lexicographic scoring for determinism.
        sc_key = (-(margin), -(progress), my_next, dx, dy)
        if best_sc is None or sc_key < best_sc:
            best_sc = sc_key
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]