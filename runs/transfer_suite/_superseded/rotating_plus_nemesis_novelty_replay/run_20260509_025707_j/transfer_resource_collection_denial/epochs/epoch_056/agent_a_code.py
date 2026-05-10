def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Find the resource that gives best "race advantage" from this move.
        # Key: maximize advantage; then minimize our distance; then prefer farther opponent distance (late tie-break).
        local_best = None  # (adv, -opp_d, -sd, sd, rx, ry)
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            k = (adv, -od, -sd, sd)
            if local_best is None or k > local_best:
                local_best = k
        if local_best is None:
            continue

        # Additional deterministic anti-deadlock: favor moves that reduce distance to our current "best resource".
        # We approximate by using sd from the local_best (its 4th element).
        adv, neg_od, neg_sd, sd = local_best
        # Small bias toward staying near center-ish to reduce corner trap when leads are small.
        center_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)

        global_key = (adv, neg_od, -sd, center_bias, dx, dy)
        if best_key is None or global_key > best_key:
            best_key = global_key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]