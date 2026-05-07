def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    best_rx = best_ry = None
    best_adv = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        if (adv > best_adv) or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < (best_rx, best_ry)))):
            best_adv = adv
            best_ds = ds
            best_rx, best_ry = rx, ry

    if best_rx is None:
        return [0, 0]

    tx, ty = best_rx, best_ry
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (-10**18, None, None, None)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # Prefer maximizing advantage, then minimizing distance to target, then tie-break deterministically by move.
        cand = (adv2, -ds2, -cheb(nx, ny, ox, oy), dx, dy)
        if cand > best:
            best = cand

    return [best[3], best[4]]