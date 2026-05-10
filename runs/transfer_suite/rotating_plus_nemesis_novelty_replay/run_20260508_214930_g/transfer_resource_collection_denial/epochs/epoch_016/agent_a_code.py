def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    best_key = None
    tx = ty = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd  # positive => we are closer or equal
        center = cheb(rx, ry, cx, cy)
        key = (win, -myd, -center, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    if tx is None:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    chosen = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        win = oppd - myd
        dist_c = cheb(nx, ny, cx, cy)
        key = (win, -myd, -dist_c, dx, dy)
        if best is None or key > best:
            best = key
            chosen = (dx, dy)

    return [chosen[0], chosen[1]]