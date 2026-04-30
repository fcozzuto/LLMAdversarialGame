def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def sgn(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
        dx = sgn(tx - sx)
        dy = sgn(ty - sy)
        candidates = []
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if legal(nx, ny):
                candidates.append((cheb(nx, ny, tx, ty), mx, my))
        if not candidates:
            return [0, 0]
        _, bestx, besty = min(candidates, key=lambda t: (t[0], t[1], t[2]))
        return [bestx, besty]

    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if legal(nx, ny):
            candidates.append((-cheb(nx, ny, ox, oy), mx, my))
    if not candidates:
        return [0, 0]
    _, bestx, besty = min(candidates, key=lambda t: (t[0], t[1], t[2]))
    return [bestx, besty]