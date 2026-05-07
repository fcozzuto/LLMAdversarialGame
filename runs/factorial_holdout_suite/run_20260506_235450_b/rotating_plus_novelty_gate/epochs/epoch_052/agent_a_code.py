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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

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
        if (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive if I'm closer
        key = (adv, -sd, -cheb(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # primary: get to target fast; secondary: keep advantage / reduce opponent chance
        score = (-(nsd), -(nod - nsd), -cheb(ox, oy, nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)
    return [best_m[0], best_m[1]]