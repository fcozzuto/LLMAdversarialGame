def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = (cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny), -cheb(nx, ny, cx, cy))
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_closest = 10**9
        opp_closest = 10**9
        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dmy < my_closest:
                my_closest = dmy
            if dop < opp_closest:
                opp_closest = dop
        # Prefer states where we can secure a resource sooner than opponent, and not stand still when behind.
        behind = (opp_closest - my_closest)
        val = (behind, -my_closest, opp_closest, -cheb(nx, ny, cx, cy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]