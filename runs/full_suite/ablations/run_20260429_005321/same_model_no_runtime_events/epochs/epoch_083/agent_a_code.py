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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    target = None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = dist(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
                bestd = d
                target = (rx, ry)
    else:
        target = (ox, oy)

    tx, ty = target
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        score = (0 if resources else 1, d, nx, ny)
        if best is None or score < best[0]:
            best = (score, [dx, dy])
    if best is None:
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return best[1]