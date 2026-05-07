def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    occ = set()
    for x, y in obstacles:
        occ.add((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, drift toward center.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if abs(tx - sx) < 1e-9 else (1 if tx > sx else -1)
        dy = 0 if abs(ty - sy) < 1e-9 else (1 if ty > sy else -1)
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                return [int(mx), int(my)]
        return [0, 0]

    # Pick resource with smallest (our distance, but prefer those we beat opponent on).
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Larger advantage is better; also tie-break by closer for us.
        adv = od - myd
        key = (-adv, myd, (rx - sx) ** 2 + (ry - sy) ** 2)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in occ:
            continue
        d = dist((nx, ny), (tx, ty))
        # Prefer reducing distance to target, and avoid getting too close to opponent.
        opp_close = max(0, 4 - dist((nx, ny), (ox, oy)))
        val = (d, opp_close, (mx == 0 and my == 0), (abs(nx - tx) + abs(ny - ty)))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]