def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

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

    if not resources:
        return [0, 0]

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Choose resource that we can reach soon and that we also "deny" (increase opponent distance).
        # Deterministic: first by highest key.
        local_best = None
        local_key = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Weighted to keep us on track while discouraging opponent access to the same target.
            # Also slightly prefer moves that reduce both distances (avoid "chasing" too far off).
            key = (-myd, (opd - myd), -(abs(nx - rx) + abs(ny - ry)) * 0.01, rx + ry)
            if local_key is None or key > local_key:
                local_key = key
                local_best = (rx, ry)

        # If for some reason none were valid (all blocked), just head to center.
        if local_key is None:
            tx, ty = w // 2, h // 2
            myd = cheb(nx, ny, tx, ty)
            local_key = (-myd, 0, 0, nx + ny)

        # Tie-break: prefer reducing distance to opponent as a mild interceptor behavior.
        interceptor = cheb(nx, ny, ox, oy)
        final_key = (local_key[0], local_key[1], local_key[2], -interceptor, local_best[0] + local_best[1] if local_best else 0, dx, dy)

        if best_key is None or final_key > best_key:
            best_key = final_key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]