def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    if resources:
        best = None
        for tx, ty in resources:
            myd = man(sx, sy, tx, ty)
            opd = man(ox, oy, tx, ty)
            adv = opd - myd  # positive means we are closer
            key = (-adv, myd, tx, ty)  # prefer larger advantage; then closer
            if best is None or key < best[0]:
                best = (key, tx, ty)
        tx, ty = best[1], best[2]
    else:
        tx, ty = sx, sy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)
    best_key = None
    opd = man(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        newd = man(nx, ny, tx, ty)
        # minimize "our lateness" relative to opponent; slight bias toward staying central to avoid jams
        central_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        key = (newd - opd, newd, central_bias, tx != nx or ty != ny, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    if dx is None:
        return [0, 0]
    return [int(dx), int(dy)]