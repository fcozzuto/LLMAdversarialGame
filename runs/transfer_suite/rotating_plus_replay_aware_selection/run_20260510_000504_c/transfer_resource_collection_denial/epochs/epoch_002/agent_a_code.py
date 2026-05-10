def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_move = (0, 0)

    if resources:
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny):
                continue
            best_here = -10**18
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources opponent is less able to reach, then be close ourselves.
                val = (od - sd) * 1000 - sd
                if val > best_here:
                    best_here = val
            # If resources list had odd entries, fallback to center-ish score.
            if best_here == -10**18:
                best_here = -(cheb(nx, ny, (w - 1) / 2, (h - 1) / 2))
            if best is None or best_here > best:
                best, best_move = best_here, (dxm, dym)
    else:
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny):
                continue
            # No resources: maximize distance from opponent; tie-break by closeness to center.
            od = cheb(nx, ny, ox, oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            val = od * 10 - dc * 0.01
            if best is None or val > best:
                best, best_move = val, (dxm, dym)

    return [best_move[0], best_move[1]]