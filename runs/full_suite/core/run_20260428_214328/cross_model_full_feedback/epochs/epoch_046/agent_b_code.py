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
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None

    # Helper to distance to a point using Chebyshev
    def dist(a, b):
        return cheb(a[0], a[1], b[0], b[1])

    # Strategy:
    # 1) Move toward nearest resource if available and not blocked.
    # 2) Else move to maximize distance from opponent while staying safe.
    if res:
        # find nearest resource
        nearest = min(res, key=lambda p: dist((sx, sy), p))
        tx, ty = nearest
        # choose move that reduces distance to target and is valid
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            if (nx, ny) in obst:
                continue
            d = dist((nx, ny), (tx, ty))
            score = -d  # closer is better
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]
        # if blocked, fall back below
    # Fall back: move that increases distance to opponent, prefer not to step into obstacle
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # prefer not to stay if opponent far; maximize distance
        d = dist((nx, ny), (ox, oy))
        score = d
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # If all else fails, stay or minor move not colliding
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
    return [0, 0]