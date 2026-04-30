def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    blocked = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Obstacle proximity penalty (avoid being adjacent to obstacles)
    obs_pen = {}
    for dx, dy, nx, ny in moves:
        p = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in blocked:
                p += 1
        obs_pen[(dx, dy, nx, ny)] = p

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            score = cheb(nx, ny, tx, ty) + 0.15 * cheb(nx, ny, ox, oy) + 0.6 * obs_pen[(dx, dy, nx, ny)]
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose move maximizing resource advantage: (opp_dist - self_dist) for the best contested resource.
    # Deterministic tie-breaks.
    best = None
    for dx, dy, nx, ny in moves:
        best_adv = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher means we're closer than opponent
            if best_adv is None or adv > best_adv:
                best_adv = adv
            elif adv == best_adv:
                # prefer resources with smaller self distance among equals
                if ds < cheb(nx, ny, best_rx, best_ry):
                    best_adv = adv
        # secondary: if same best_adv, reduce self distance to that resource (recompute by min ds where adv==best_adv)
        tie_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do - ds == best_adv:
                if tie_ds is None or ds < tie_ds:
                    tie_ds = ds
        score = (-best_adv, tie_ds if tie_ds is not None else 0, obs_pen[(dx, dy, nx, ny)], dx, dy)
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]