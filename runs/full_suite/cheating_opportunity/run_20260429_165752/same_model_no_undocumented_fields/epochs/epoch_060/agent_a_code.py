def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w)
    h = int(h)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        tx, ty = resources[0]
        bestd = dist(sx, sy, tx, ty)
        for x, y in resources[1:]:
            d = dist(sx, sy, x, y)
            if d < bestd or (d == bestd and (x < tx or (x == tx and y < ty))):
                bestd, tx, ty = d, x, y
    else:
        tx, ty = w // 2, h // 2

    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        score = (d, dist(nx, ny, ox, oy))
        if best is None or score < bestscore:
            bestscore = score
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]