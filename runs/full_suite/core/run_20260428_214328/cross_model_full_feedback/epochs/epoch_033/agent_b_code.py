def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def collides(nx, ny): return (nx, ny) in obst or (nx, ny) == (ox, oy)
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collides(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If there are resources, target nearest one with simple tie-breaker
    if res:
        best = None
        bestd = 10**9
        for dx, dy, nx, ny in legal:
            # distance to closest resource
            d = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No resources or no good resource path: move to maximize distance from opponent
    best = None
    bestv = -10**9
    for dx, dy, nx, ny in legal:
        v = cheb(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]