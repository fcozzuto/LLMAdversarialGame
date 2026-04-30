def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        tx, ty = resources[0]
        bestd = cheb(sx, sy, tx, ty)
        for (x, y) in resources[1:]:
            d = cheb(sx, sy, x, y)
            if d < bestd or (d == bestd and (y < ty or (y == ty and x < tx))):
                bestd, tx, ty = d, x, y
    else:
        tx, ty = ox, oy

    best = None
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            dist_to_t = cheb(nx, ny, tx, ty)
            dist_to_op = cheb(nx, ny, ox, oy)
            score = (-dist_to_t, dist_to_op, nx, ny)
        else:
            dist_from_op = cheb(nx, ny, ox, oy)
            score = (dist_from_op, -nx, -ny)
        if bestscore is None or score > bestscore:
            bestscore, best = score, [dx, dy]
    if best is None:
        return [0, 0]
    return best