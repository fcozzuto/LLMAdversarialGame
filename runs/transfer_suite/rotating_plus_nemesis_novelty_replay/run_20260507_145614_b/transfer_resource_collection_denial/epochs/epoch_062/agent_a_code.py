def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose a target that we can realistically beat, otherwise deny opponent by going to a contested/nearby cell.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer resources where we are not losing; break ties by smaller sd.
        # If we are losing, still go to something where opponent is also far, to reduce their sweep opportunities.
        win_bias = od - sd
        lose_pen = 1 if sd > od else 0
        key = (lose_pen, -win_bias, sd, abs(rx - sx) + abs(ry - sy))
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    rx, ry = best
    # If we're adjacent, take it (engine will handle if occupied resource is gone next tick).
    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Pick the next move that maximizes advantage swing toward the chosen target.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = md(nx, ny, rx, ry)
        od2 = md(ox, oy, rx, ry)
        # Also lightly prefer moves that reduce potential "trap" by keeping mobility.
        mob = 0
        for ex, ey in moves:
            xx, yy = nx + ex, ny + ey
            if inb(xx, yy):
                mob += 1
        # Primary: maximize (od2 - sd2). Secondary: minimize sd2. Tertiary: higher mobility.
        mkey = (- (od2 - sd2), sd2, -mob, abs((nx - rx)) + abs((ny - ry)))
        if best_mkey is None or mkey < best_mkey:
            best_mkey, best_move = mkey, (dx, dy)

    return [best_move[0], best_move[1]]