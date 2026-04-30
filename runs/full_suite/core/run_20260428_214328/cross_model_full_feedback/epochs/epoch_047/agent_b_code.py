def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

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

    def dist_to_point(px, py):
        return cheb(px, py, ox, oy)

    # Heuristic:
    # 1) If there is a resource not blocked, move toward the closest one.
    # 2) If none, maximize distance from opponent; break ties by moving closer to a resource if any visible in line.
    target = None
    if res:
        # choose nearest resource by Chebyshev
        best_r = None
        best_d = None
        for (rx, ry) in res:
            d = cheb(sx, sy, rx, ry)
            if best_d is None or d < best_d:
                best_d = d
                best_r = (rx, ry)
        target = best_r

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        val = 0
        # prefer moving towards target
        if target is not None:
            val += -cheb(nx, ny, target[0], target[1])
        # prefer moving away from opponent
        od = cheb(nx, ny, ox, oy)
        val += od
        # prefer staying if blocked options equal
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If no valid move found (highly unlikely), stay
    dx, dy = best_move
    if dx is None or dy is None:
        dx, dy = 0, 0
    return [dx, dy]