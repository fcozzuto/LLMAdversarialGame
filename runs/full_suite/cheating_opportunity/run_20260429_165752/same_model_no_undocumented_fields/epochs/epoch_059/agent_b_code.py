def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            key = (dS - dO, dS, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        rx, ry = best
        curd = cheb(sx, sy, rx, ry)
        cand = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                nd = cheb(nx, ny, rx, ry)
                cand.append((nd, dx, dy))
        cand.sort()
        for nd, dx, dy in cand:
            if nd < curd:
                return [dx, dy]
        for nd, dx, dy in cand:
            if (dx, dy) == (0, 0):
                return [dx, dy]
        return [cand[0][1], cand[0][2]]
    else:
        tx, ty = w // 2, h // 2
        curd = cheb(sx, sy, tx, ty)
        cand = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                nd = cheb(nx, ny, tx, ty)
                cand.append((nd, dx, dy))
        cand.sort()
        for nd, dx, dy in cand:
            if nd < curd:
                return [dx, dy]
        return [0, 0]