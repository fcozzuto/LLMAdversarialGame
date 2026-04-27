def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_target():
        return (w - 1) // 2, (h - 1) // 2

    tx, ty = center_target()
    if resources:
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            my_best = 10**9
            op_best = 10**9
            for rx, ry in resources:
                d1 = cd(nx, ny, rx, ry)
                if d1 < my_best:
                    my_best = d1
                d2 = cd(ox, oy, rx, ry)
                if d2 < op_best:
                    op_best = d2
            # Prefer getting closer to resources, especially ones opponent is not closer to.
            # Tie-break deterministically by dx,dy.
            key = (my_best, -op_best, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cd(nx, ny, tx, ty)
            # Tie-break to drift toward opponent deterministically.
            key = (d, -(nx - ox), -(ny - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]