def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Drift target if no resources
    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d_op = abs(nx - ox) + abs(ny - oy)
            d_ctr = abs(nx - cx) + abs(ny - cy)
            val = (d_op) - 0.08 * d_ctr
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    res_set = set((r[0], r[1]) for r in resources)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Immediate reward for collecting if resource present at landing cell.
        immediate = 3.0 if (nx, ny) in res_set else 0.0
        # Risk/reward: prefer cells where we are closer than opponent to some resource.
        best_margin = -10.0
        best_self = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            margin = d_opp - d_self  # higher is better for us
            if margin > best_margin:
                best_margin = margin
            if d_self < best_self:
                best_self = d_self
        # Avoid getting too close to opponent unless it helps margin.
        d_op = cheb(nx, ny, ox, oy)
        avoid = -0.15 / (1 + d_op)
        val = immediate + (2.2 * best_margin) - (0.18 * best_self) + avoid
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]