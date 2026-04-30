def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        if r is None:
            continue
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = target
        best = None
        for dx, dy, nx, ny in legal:
            d_me = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            cand = (d_me, -d_opp, dx, dy, nx, ny)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]]

    best = None
    for dx, dy, nx, ny in legal:
        d_opp = cheb(nx, ny, ox, oy)
        cand = (-d_opp, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[1], best[2]]