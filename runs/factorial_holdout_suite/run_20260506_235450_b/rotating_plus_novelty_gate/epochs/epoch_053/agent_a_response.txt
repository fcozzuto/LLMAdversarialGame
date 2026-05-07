def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obs

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
    else:
        best = None
        best_key = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not isinstance(rx, int) or not isinstance(ry, int):
                continue
            if blocked(rx, ry):
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            nearest_self = sd
            key = (adv, -nearest_self, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        if best is None:
            tx, ty = (w - 1, h - 1)
        else:
            tx, ty = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)  # slight bias to avoid being directly adjacent to opponent
        score = (-nsd, nod, -abs((nx + ny) - (tx + ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]