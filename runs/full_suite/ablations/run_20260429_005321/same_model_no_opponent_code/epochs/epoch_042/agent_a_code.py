def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Pick target where self is significantly closer than opponent; include tie-breakers.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds
        key = (margin, -ds, ds - do, -rx - ry, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    # Local move: choose among 9 deltas deterministically.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside_free(nx, ny):
            continue
        d1 = cheb(nx, ny, rx, ry)
        d2 = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: stay farther from opponent; Tertiary: deterministic.
        key = (-d1, d2, -abs((nx - ox)) - abs((ny - oy)), dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))
    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]