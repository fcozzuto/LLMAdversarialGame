def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and not blocked(rx, ry):
                valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best = None
    bestv = 10**9
    for rx, ry in valid:
        d = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = d + (0 if do > d else 2)  # prefer resources likely not reachable faster by opponent
        if score < bestv:
            bestv = score
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if not blocked(nx, ny):
                moves.append((mx, my, nx, ny))

    curd = cheb(sx, sy, tx, ty)
    bestm = (0, 0, curd, 10**9)
    for mx, my, nx, ny in moves:
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(ox, oy, tx, ty)
        # minimize self distance; slightly penalize moves that let opponent be closer to the target
        val = (dself, -(dop - dself))
        if val < (bestm[2], bestm[3]):
            bestm = (mx, my, dself, dop - dself)

    return [int(bestm[0]), int(bestm[1])]