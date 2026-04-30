def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If adjacent to any resource, take the best one.
    best_adj = None
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        d = cheb(sx, sy, rx, ry)
        if d <= 1:
            score = cheb(ox, oy, rx, ry) - d
            if best_adj is None or (score, -rx, -ry) > (best_adj[0], -best_adj[1], -best_adj[2]):
                best_adj = (score, rx, ry)
    if best_adj is not None:
        _, rx, ry = best_adj
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            return [dx, dy]

    # Strategy: move toward a resource we can reach sooner than the opponent, while discouraging opponent access.
    best_move = (None, None, None)  # (score, nx, ny)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        if not resources:
            # Deterministic retreat to center-ish if no resources.
            cx, cy = w // 2, h // 2
            score = -cheb(nx, ny, cx, cy)
            if best_move[0] is None or score > best_move[0]:
                best_move = (score, nx, ny)
            continue

        # Evaluate best target for this candidate move.
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer: maximize "we can arrive first"; also prefer actual progress (smaller ds).
            # Add small term to prioritize nearer resources deterministically.
            val = (do - ds) * 1000 - ds * 3 - cheb(nx, ny, rx, ry)
            if local_best is None or (val, -rx, -ry) > local_best:
                local_best = (val, rx, ry)
        if local_best is None:
            continue
        val, _, _ = local_best
        # Tie-break: slightly prefer moves that reduce distance to opponent targetless (keep separation).
        sep = cheb(nx, ny, ox, oy)
        score = (val, -sep)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, nx, ny)

    if best_move[1] is None:
        return [0, 0]
    dx = best_move[1] - sx
    dy = best_move[2] - sy
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [int(dx), int(dy)]