def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield dx, dy, nx, ny

    def nearest_corner(px, py):
        best = None
        bestd = None
        for cx, cy in corners:
            d = cheb(px, py, cx, cy)
            if bestd is None or d < bestd:
                bestd = d
                best = (cx, cy)
        return best

    # Pursuit target: where opponent likely wants to go (nearest corner).
    ocx, ocy = nearest_corner(ox, oy)
    # Intercept bias: aim slightly toward the opponent corner while still reducing distance.
    tx, ty = ocx, ocy

    best = None
    best_key = None
    for dx, dy, nx, ny in legal_moves(sx, sy):
        d_op = cheb(nx, ny, ox, oy)
        d_tx = cheb(nx, ny, tx, ty)
        # obstacle-avoidance heuristic: prefer cells with more free immediate options
        free = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay):
                free += 1

        if is_pursuer:
            # primary: minimize distance to opponent; secondary: drift toward predicted corner; tertiary: keep options
            key = (d_op, d_tx, -free)
        else:
            # evader: maximize distance; secondary: drift toward farthest corner from pursuer; tertiary: keep options
            fc = None
            fcd = None
            for cx, cy in corners:
                d = cheb(ox, oy, cx, cy)
                if fcd is None or d > fcd:
                    fcd = d
                    fc = (cx, cy)
            fcx, fcy = fc
            d_far = cheb(nx, ny, fcx, fcy)
            key = (-d_op, -d_far, -free)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]