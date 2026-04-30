def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    t = observation.get("turn_index", 0)
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

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

    def legal_moves(x, y):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                yield dx, dy, nx, ny

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    best = (0, 0)
    bestv = -10**18

    # If no resources, drift to safer center while moving away from opponent.
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        if (t % 2) == 1:
            cx = w - 1 - cx
        for dx, dy, nx, ny in legal_moves(sx, sy):
            v = 0.7 * cheb(nx, ny, ox, oy) - 0.3 * cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Greedy one-step race/denial: prefer resources where we are closer than opponent.
    for dx, dy, nx, ny in legal_moves(sx, sy):
        my_best = -10**18
        for rx, ry in res:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Denial term: larger when we are closer than opponent.
            # Progress term: encourage smaller our distance.
            v = (d_op - d_me) * 2.0 - d_me * 0.35
            # Tiny deterministic bias so ties break consistently.
            v -= 0.01 * (abs(rx - w // 2) + abs(ry - h // 2))
            if v > my_best:
                my_best = v
        if my_best > bestv:
            bestv, best = my_best, (dx, dy)

    return [best[0], best[1]]