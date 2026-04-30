def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                res.append((rx, ry))

    def dist(a, b):
        d = a - b
        if d < 0:
            d = -d
        return d

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tx, ty = sx, sy
    if res:
        best = None
        for rx, ry in res:
            v = cheb(sx, sy, rx, ry)
            if best is None or v < best[0] or (v == best[0] and (rx, ry) < best[1]):
                best = (v, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move, best_score = (0, 0), None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        to_t = cheb(nx, ny, tx, ty)
        to_o = cheb(nx, ny, ox, oy)
        score = (to_t, -to_o, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0] and not inb(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
    return best_move