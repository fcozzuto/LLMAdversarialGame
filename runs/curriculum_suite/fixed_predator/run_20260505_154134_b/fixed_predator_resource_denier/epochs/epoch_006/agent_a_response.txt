def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_score(px, py):
        if resources:
            best = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                self_d = cheb((px, py), (rx, ry))
                opp_d = cheb((ox, oy), (rx, ry))
                # Primary: win-by-distance margin; then prefer smaller self distance; then favor nearer to board center slightly.
                margin = opp_d - self_d
                center_bias = -((abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01)
                val = (margin, -self_d, center_bias, rx, ry)
                if best is None or val > best[0]:
                    best = (val, None)
            if best is not None:
                return best[0]
        # No usable resources: deny by moving closer to opponent (reduce their options).
        dself = cheb((px, py), (ox, oy))
        return (-dself, 0, 0, 0, 0)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        v = cell_score(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    if best_val is None:
        # All safe moves blocked: pick a bounded move that minimizes distance to opponent, still avoiding obstacles if possible.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (-cheb((nx, ny), (ox, oy)), -man((nx, ny), (ox, oy)))
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    return [best_move[0], best_move[1]]