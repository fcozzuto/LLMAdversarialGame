def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                ok = True
            else:
                ok = in_bounds(nx, ny) and (nx, ny) not in obstacles
            if ok and in_bounds(nx, ny):
                moves.append((dx, dy))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # pick resource where we are (deterministically) closer than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds)  # positive means we can reach sooner
        key = (-score, ds, rx, ry)  # choose largest score, then smallest ds, then stable tie
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # choose move that most reduces distance to target, with obstacle safety already handled
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), (tx, ty))
        # slight preference: diagonals over straight if equal; stable tie by dx,dy
        diag = 1 if dx != 0 and dy != 0 else 0
        key = (d, -diag, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]