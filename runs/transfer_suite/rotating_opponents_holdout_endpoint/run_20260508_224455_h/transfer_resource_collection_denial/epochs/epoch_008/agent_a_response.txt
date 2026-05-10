def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None  # (key, tx, ty) where key smaller is worse; we want max advantage so use negative.
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        adv = opd - myd  # positive => we are closer
        # Prefer greater advantage; then closer by tie-break.
        key = (-adv, myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda m: (0 if m == (0, 0) else 1, -abs(m[0]) - abs(m[1])))

    def score_move(nx, ny):
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Lower is better: reduce our distance, and increase current advantage.
        adv = opd - myd
        return (myd, -adv, nx, ny)

    chosen = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            if chosen is None or score_move(nx, ny) < chosen[0]:
                chosen = (score_move(nx, ny), dx, dy)

    if chosen is None:
        return [0, 0]
    return [chosen[1], chosen[2]]