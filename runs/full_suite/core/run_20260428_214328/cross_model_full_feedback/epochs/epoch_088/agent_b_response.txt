def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If there are resources, move toward the closest resource while avoiding obstacles.
    if resources:
        sxr, syr = sx, sy
        best = None
        bestd = 10**9
        for r in resources:
            d = cheb((sxr, syr), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None:
            dx = 1 if best[0] > sx else -1 if best[0] < sx else 0
            dy = 1 if best[1] > sy else -1 if best[1] < sy else 0
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
            # try alternative in order of closeness
            for adx, ady in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
                tx, ty = sx + adx, sy + ady
                if valid(tx, ty):
                    return [adx, ady]
    # If no resources or blocked, pursue center while keeping corridor with opponent in mind
    center = ((w - 1) // 2, (h - 1) // 2)
    dx = 1 if center[0] > sx else -1 if center[0] < sx else 0
    dy = 1 if center[1] > sy else -1 if center[1] < sy else 0
    # try to move toward center if possible, else try small adjustments
    if valid(sx + dx, sy + dy):
        return [dx, dy]
    for adx, ady in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = sx + adx, sy + ady
        if valid(nx, ny):
            return [adx, ady]
    # As a fallback stay
    return [0, 0]