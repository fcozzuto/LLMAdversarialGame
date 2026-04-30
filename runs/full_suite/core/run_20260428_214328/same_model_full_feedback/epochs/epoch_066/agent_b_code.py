def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = sx, sy
    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            v = (opd - myd) * 1000 - myd
            if best is None or v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_dist = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)
        elif d == best_dist:
            if man(nx, ny, ox, oy) > man(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = (dx, dy)

    if not ok(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]