def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    cx, cy = w // 2, h // 2

    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dcen = dist(nx, ny, cx, cy)
            dstep = dist(nx, ny, ox, oy)
            key = (dcen, dstep, dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer resources where we have reach advantage over opponent
        best_adv = -10**9
        best_res_d = 10**9
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive means we get there no later
            if adv > best_adv or (adv == best_adv and (ds < best_res_d or (ds == best_res_d and (rx + ry) < (best_res_d)))):
                best_adv = adv
                best_res_d = ds

        # Convert to a minimization key: maximize adv, then minimize our distance, then prefer moves toward center
        dcenter = dist(nx, ny, cx, cy)
        own_d_near = best_res_d
        # Include slight preference to reduce distance to opponent to contest fast paths deterministically
        d_to_opp = dist(nx, ny, ox, oy)
        key = (-best_adv, own_d_near, dcenter, d_to_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]