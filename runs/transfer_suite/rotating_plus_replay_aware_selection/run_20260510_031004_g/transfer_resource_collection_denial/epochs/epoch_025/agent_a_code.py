def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))
        except:
            pass

    resources = []
    for p in (observation.get("resources") or []):
        try:
            resources.append((int(p[0]), int(p[1])))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    target = resources[0]
    bestd = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)

    sx0, sy0 = sx, sy
    tx, ty = target
    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in steps:
        nx, ny = sx0 + dx, sy0 + dy
        if not free(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        score = (-myd, -od, dx, dy)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]