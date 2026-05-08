def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my = (nx, ny)
        my_best = None
        for rx, ry in res:
            myd = md(my, (rx, ry))
            opd = md((ox, oy), (rx, ry))
            margin = opd - myd  # positive means we are closer
            # Prefer taking resources we can reach first; otherwise block closest-to-opponent.
            val = margin * 100 - myd + (opd * 0.1)
            if my_best is None or val > my_best:
                my_best = val
        if best_val is None or my_best > best_val or (my_best == best_val and (dx, dy) < best_move):
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]