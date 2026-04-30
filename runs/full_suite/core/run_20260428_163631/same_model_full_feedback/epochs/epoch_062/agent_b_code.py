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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_t = None
    best_s = -10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        s = (od - md) * 100 - md + (rx * 2 + ry) * 1e-6
        if s > best_s:
            best_s = s
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = [0, 0]
    best_ms = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        ms = (opd - myd) * 100 - myd
        if ms > best_ms:
            best_ms = ms
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]