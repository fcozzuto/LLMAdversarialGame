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

    def cheb(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    best_move = None
    best_score = None

    # If there are resources, try to move toward the closest resource not blocked
    if res:
        # choose resource with minimal chebyshev distance to candidate square, then closer to us
        target = None
        best_rdist = None
        for rx, ry in res:
            # find best legal move toward (rx, ry)
            # score: -cheb(new, target) where target is resource
            for dx, dy, nx, ny in legal:
                d = cheb(nx, ny, rx, ry)
                if best_rdist is None or d < best_rdist:
                    best_rdist = d
                    best_move = [dx, dy]
                    target = (rx, ry)
        if best_move is not None:
            return best_move

    # If no visible resources, or none chosen, move to increase distance from opponent
    # Pick legal move that maximizes distance to opponent; break ties by staying closer to center
    best_move = None
    best_dist = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, ox, oy)
        if best_dist is None or d > best_dist:
            best_dist = d
            best_move = [dx, dy]
    if best_move is not None:
        return best_move

    return [0, 0]