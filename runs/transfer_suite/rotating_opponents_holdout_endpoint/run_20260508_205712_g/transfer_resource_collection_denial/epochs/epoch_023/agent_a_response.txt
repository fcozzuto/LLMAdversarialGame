def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    tx, ty = resources[0]
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        swing = opd - myd  # prefer targets where we are closer (swing larger)
        center = - (abs(rx - cx) + abs(ry - cy))
        key = (swing, -myd, center)
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_delta = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # Primary: reduce our distance to target. Secondary: keep advantage vs opponent.
        val = (-myd2, (opd2 - myd2), -max(abs(nx - (w - 1) / 2.0), abs(ny - (h - 1) / 2.0)))
        if best_m is None or val > best_m:
            best_m = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]