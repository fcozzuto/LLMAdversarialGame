def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and not (nx == ox and ny == oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)

    def nearest_resource(nx, ny):
        if not res:
            return None
        best = None
        bestd = None
        for (rx, ry) in res:
            d = dist((nx, ny), (rx, ry))
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        return best

    # Prefer moving toward nearest resource if safe, else approach opponent while avoiding obstacle
    nr = nearest_resource(sx, sy)
    if nr is not None:
        tx, ty = nr
        # choose move that minimizes chebyshev distance to resource
        best = None; bestd = None
        for dx, dy, nx, ny in legal:
            d = dist((nx, ny), (tx, ty))
            if bestd is None or d < bestd:
                bestd = d; best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move toward opponent if not blocked, else stay
    # pick move that reduces Chebyshev distance to opponent while not stepping into obstacle
    best = None; bestd = None
    for dx, dy, nx, ny in legal:
        d = dist((nx, ny), (ox, oy))
        if bestd is None or d < bestd:
            bestd = d; best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]