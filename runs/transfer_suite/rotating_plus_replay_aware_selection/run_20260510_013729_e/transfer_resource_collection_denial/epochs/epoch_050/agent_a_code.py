def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Deterministic ordering: closest-ish by x,y then by distance
    res_sorted = sorted(resources, key=lambda p: (p[0] * 16 + p[1], p[0], p[1]))

    # Score a potential target resource: want positive lead; tie-break by smaller self distance.
    def target_value(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        cap = 7.0 if (sx, sy) == (rx, ry) else 0.0
        # Prefer resources we can reach earlier; add mild preference to stay away from opponent for denial.
        return cap + 2.6 * (do - ds) - 0.25 * ds + 0.10 * cheb(ox, oy, rx, ry)

    # Choose the best target deterministically
    best_t = None
    best_tv = -10**18
    for rx, ry in res_sorted:
        tv = target_value(rx, ry)
        if tv > best_tv:
            best_tv = tv
            best_t = (rx, ry)

    rx, ry = best_t

    # Evaluate immediate moves: avoid obstacles and choose move that improves lead to the target.
    def move_value(nx, ny):
        if not inb(nx, ny):
            return -10**18
        if (nx, ny) in obst:
            return -10**18
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer (good)
        # If we land on a resource, strongly prefer.
        cap = 8.0 if (nx, ny) in resources else 0.0

        # Small denial term: if opponent is closer to some other resource, discourage moving near them.
        denial = 0.0
        for (arx, ary) in res_sorted[:min(6, len(res_sorted))]:
            if (arx, ary) == (rx, ry):
                continue
            if (nx, ny) == (arx, ary):
                continue
            denial += 0.05 * (cheb(ox, oy, arx, ary) - cheb(nx, ny, arx, ary))

        # Encourage reducing distance to chosen target.
        return cap + 2.9 * lead - 0.35 * ds + denial + 0.02 * (cheb(nx, ny, ox, oy))

    # Deterministic tie-break via (value, -progress, x, y)
    best_m = (0, 0)
    best_mv = -10**18
    best_prog = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        mv = move_value(nx, ny)
        if mv <= -10**17:
            continue
        prog = cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry)
        # Tie-break deterministically
        key = (mv, prog, -nx, -ny)
        key_best = (best_mv, best_prog, - (sx + best_m[0]), - (sy + best_m[1]))
        if key > key_best:
            best_mv = mv
            best_prog = prog
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]