def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource: maximize our advantage (opponent-time - our-time), tie-break by being closer and safer.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are earlier/at least not later
            # If both are close, also prefer resource that keeps distance spread (more likely uncontested).
            spread = abs(do - ds)
            edge_bonus = 1 if (rx == 0 or ry == 0 or rx == w - 1 or ry == h - 1) else 0
            key = (adv, spread, -ds, edge_bonus)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No known resources: drift toward center to reduce being outflanked.
        tx, ty = (w // 2, h // 2)

    # Obstacle-aware local move toward target; break ties deterministically by preferring no-diagonal then straights.
    # Bias: don't step into obstacle; also avoid increasing distance to target too much.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer smaller distance; second: also reduce opponent distance to that target (discourage giving up spots).
        do_new = cheb(ox, oy, tx, ty)
        # Small deterministic tie-break: favor orthogonal/less movement magnitude.
        mag = abs(dx) + abs(dy)
        val = (-d, -(d - (do_new // 2)), -mag, dx == 0 and dy == 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]