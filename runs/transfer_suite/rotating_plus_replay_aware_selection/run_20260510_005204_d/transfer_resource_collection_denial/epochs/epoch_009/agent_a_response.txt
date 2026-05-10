def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (8-dir)

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Prefer resources where we are closer; break ties by closer distance and nearer to center.
        center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
        key = (opd - myd, -myd, center_bias, -rx - ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None
    myd0 = cd(sx, sy, tx, ty)
    opd0 = cd(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd1 = cd(nx, ny, tx, ty)
        # Reduce opponent advantage by choosing moves that increase our relative progress.
        my_progress = myd0 - myd1
        opp_progress = opd0 - cd(ox, oy, tx, ty)
        # Also lightly avoid stepping into being closer to many resources (useful when contested).
        congestion = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            congestion += 1 if cd(nx, ny, rx, ry) <= cd(ox, oy, rx, ry) else 0
        val = (myd1 == 0, my_progress + (-opp_progress), -myd1, -congestion, -abs(nx - tx) - abs(ny - ty))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]