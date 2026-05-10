def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def nearest_corner(px, py):
        bc = corners[0]
        bd = cheb(px, py, bc[0], bc[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d < bd:
                bd = d
                bc = (cx, cy)
        return bc

    def farthest_corner(px, py):
        bc = corners[0]
        bd = cheb(px, py, bc[0], bc[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d > bd:
                bd = d
                bc = (cx, cy)
        return bc

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            # Intercept-like: shrink distance; tie-break by pushing toward nearest corner (reduces evasion space).
            nc = nearest_corner(ox, oy)
            dcorner = cheb(nx, ny, nc[0], nc[1])
            sc = (-d, -dcorner, -abs(nx - ox) - abs(ny - oy))
        else:
            # Evade: maximize distance; tie-break by pushing away from opponent toward farthest corner.
            fc = farthest_corner(ox, oy)
            dcorner = cheb(nx, ny, fc[0], fc[1])
            sc = (d, dcorner, -abs(nx - ox) - abs(ny - oy))
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]