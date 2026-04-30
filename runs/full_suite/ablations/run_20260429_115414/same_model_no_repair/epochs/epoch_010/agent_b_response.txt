def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tx, ty = None, None
    if resources:
        best = None
        # Prefer resources we can reach no later than opponent; maximize (opd - myd).
        # Tie-break deterministically to stabilize routing.
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            reach_adv = opd - myd
            tie = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
            key = (reach_adv, -myd, tie, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w - 1, h - 1

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Main: increase opponent's distance advantage against them (opd2 - myd2).
        # Secondary: minimize our distance; tertiary: prefer moves that progress in our direction.
        score = (opd2 - myd2) * 1000 - myd2 * 3 + (nx + ny) * 0.001
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]