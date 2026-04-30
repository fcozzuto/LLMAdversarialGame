def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            if dx == 0 and dy == 0:
                base = 0
            else:
                base = 0

            if resources:
                myd = 10**9
                opd = 10**9
                for rx, ry in resources:
                    d1 = cheb(nx, ny, rx, ry)
                    if d1 < myd: myd = d1
                    d2 = cheb(ox, oy, rx, ry)
                    if d2 < opd: opd = d2
                val = (opd - myd) * 1000 - myd
                if dx == 0 and dy == 0:
                    val -= 1
            else:
                myd = cheb(nx, ny, ox, oy)
                val = myd
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
            elif val == best_val and best is not None:
                if (dx, dy) < best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]