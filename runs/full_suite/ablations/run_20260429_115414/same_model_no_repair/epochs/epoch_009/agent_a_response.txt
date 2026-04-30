def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources opponent can't reach much sooner; tie-break by earliest/central/lower coords.
            key = (opd - myd, -myd, -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)), -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = w - 1, h - 1

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: progress toward target
        d_to = cheb(nx, ny, tx, ty)
        d_from = cheb(sx, sy, tx, ty)
        progress = d_from - d_to

        # Secondary: safety vs opponent (bigger is better)
        d_opp = cheb(nx, ny, ox, oy)
        safety = d_opp

        # Tertiary: discourage stepping into obstacle-adjacent cells
        ob_adj = 0
        if obstacles:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        ob_adj += 1

        # If landing on a resource, strongly prefer it
        on_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break

        val = (on_res * 1000) + progress * 20 + safety * 2 - ob_adj * 5 - d_to
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]