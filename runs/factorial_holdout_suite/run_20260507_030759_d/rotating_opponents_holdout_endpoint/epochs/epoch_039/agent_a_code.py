def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer resources we can take earlier; otherwise, head to the best contested region.
    best = None
    for tx, ty in res:
        sd = cheb((sx, sy), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        # Higher is better.
        value = (od - sd, -sd, -(tx + ty))
        if best is None or value > best[0]:
            best = (value, (tx, ty))
    (value, (tx, ty)) = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        sd = cheb((nx, ny), (tx, ty))
        # If staying is allowed, favor moving toward target.
        s = (-sd, -(abs(nx - tx) + abs(ny - ty)))
        # Also prevent stepping into likely opponent sweep by biasing away from opponent direction.
        opp_bias = cheb((nx, ny), (ox, oy))
        s = (s[0], s[1], opp_bias)
        return s

    best_move = None
    best_ms = None
    # Deterministic tie-break: iterate in fixed order by dx,dy already collected.
    for dx, dy in sorted(moves):
        ms = move_score(dx, dy)
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]