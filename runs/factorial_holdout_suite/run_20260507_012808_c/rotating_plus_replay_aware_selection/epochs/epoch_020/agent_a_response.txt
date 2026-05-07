def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # If no visible resources, drift to center while avoiding opponent.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)) - 0.1 * cheb(nx, ny, cx, cy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Score each resulting move by how strongly we can secure a contested resource next.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        collected = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        # Evaluate best target resource from our perspective, penalize when opponent is closer.
        best_target_val = -10**9
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Higher is better: we want to be closer than opponent; collecting gets huge bonus.
            val = (1000 if d_me == 0 else 0) + (d_op - d_me) - 0.02 * d_me
            if val > best_target_val:
                best_target_val = val
        # Small tie-break: keep some pressure toward center rather than oscillate.
        tie = -0.03 * cheb(nx, ny, cx, cy) + 0.01 * cheb(ox, oy, nx, ny)
        total = best_target_val + (200 if collected else 0) + tie
        if best is None or total > best[0]:
            best = (total, dx, dy)
    return [best[1], best[2]]