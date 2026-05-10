def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we're already closer; otherwise prefer those with smallest handicap.
        # key: primary is (opd - myd), then prefer smaller myd, then deterministic coords.
        key = (opd - myd, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    # Secondary: if we're not closer to any resource, pull focus to "contest" near opponent.
    # Detect by scanning quickly if any resource beats opponent at our current position.
    closer_exists = False
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) < cheb(ox, oy, rx, ry):
            closer_exists = True
            break

    if not closer_exists:
        # Choose nearest resource to opponent (they are likely aiming there); go to reduce their lead.
        best2 = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            key = (-opd, (opd - myd), -myd, -rx, -ry)
            if best2 is None or key > best2[0]:
                best2 = (key, rx, ry)
        tx, ty = best2[1], best2[2]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Value: capture pressure + safety (avoid getting too close to opponent unless it helps).
        dist_opp = cheb(nx, ny, ox, oy)
        # If we can be closer than opponent after the move, prioritize strongly.
        win_pressure = (opd - myd)
        key = (win_pressure, -myd, dist_opp, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]