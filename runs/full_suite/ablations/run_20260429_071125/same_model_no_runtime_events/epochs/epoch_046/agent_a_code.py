def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    target = None
    best = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if best is None or d < best or (d == best and (rx, ry) < target):
            best = d
            target = (rx, ry)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    best_move = (0, 0)
    best_dist = None
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            d = cheb(nx, ny, tx, ty)
            if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
                best_dist = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]