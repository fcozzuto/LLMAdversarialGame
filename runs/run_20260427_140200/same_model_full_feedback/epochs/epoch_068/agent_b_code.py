def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = (0, 0)
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dmin = 10**18
            for rx, ry in resources:
                ddx = nx - rx
                if ddx < 0: ddx = -ddx
                ddy = ny - ry
                if ddy < 0: ddy = -ddy
                d = ddx if ddx > ddy else ddy
                if d < dmin: dmin = d
            v = (dmin, -(nx - ox if (nx - ox) else 0), -(ny - oy if (ny - oy) else 0))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: reduce distance to opponent (deterministic chase)
    best = (0, 0)
    bestd = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ddx = nx - ox
        if ddx < 0: ddx = -ddx
        ddy = ny - oy
        if ddy < 0: ddy = -ddy
        d = ddx if ddx > ddy else ddy
        if bestd is None or d < bestd:
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]]