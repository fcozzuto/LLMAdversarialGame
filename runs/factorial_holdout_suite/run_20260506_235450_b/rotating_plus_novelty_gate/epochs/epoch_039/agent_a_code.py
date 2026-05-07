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
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    has_res = len(resources) > 0
    if has_res:
        tx, ty = resources[0]
        bestd = cheb(sx, sy, tx, ty)
        for rx, ry in resources[1:]:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd, tx, ty = d, rx, ry
    else:
        tx, ty = ox, oy

    curd = cheb(sx, sy, tx, ty)
    best = None
    bestv = -10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        v = (curd - d) * 100
        if has_res:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    v += 10**6
        else:
            v += -(cheb(nx, ny, ox, oy))
        if v > bestv or (v == bestv and best is None):
            bestv = v
            best = [dx, dy]
    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best