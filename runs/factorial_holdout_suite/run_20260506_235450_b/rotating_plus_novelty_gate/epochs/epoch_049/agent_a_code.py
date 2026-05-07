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
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if not inside(rx, ry) and (rx, ry) not in obs:
            pass
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best
    curd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_dist = curd
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]