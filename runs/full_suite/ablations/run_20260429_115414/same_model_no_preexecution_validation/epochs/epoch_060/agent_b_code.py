def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a resource that is good for us: far from opponent and reasonably close to us.
    best = None
    best_sc = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if opd <= myd:
            # If opponent is at least as close, de-prioritize strongly.
            sc = -1000 + opd - myd
        else:
            sc = 5 * (opd - myd) - myd
        # Deterministic tie-breaker: lexicographic then myd
        key = (-sc, myd, rx, ry)
        if best is None or key < best_sc:
            best = (rx, ry)
            best_sc = key

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Obstacle proximity penalty to reduce risk of getting stuck near obstacles
        obst_pen = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (nx + ddx, ny + ddy) in obstacles:
                        obst_pen += 1
        # Also discourage moving into squares that are "closer" to opponent than necessary
        sc_key = (myd, -opd, obst_pen, dx, dy)
        if best_key is None or sc_key < best_key:
            best_key = sc_key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]