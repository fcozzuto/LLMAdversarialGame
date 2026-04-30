def choose_move(observation):
    w = int(observation.get("grid_width") or 8) or 8
    h = int(observation.get("grid_height") or 8) or 8
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (1 if md <= od else 0, -(od - md), md, abs(rx - ox) + abs(ry - oy))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is not None:
        tx, ty = best_target
        best = None
        best_score = None
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, tx, ty)
            myd = cheb(sx, sy, tx, ty)
            closer = myd - d
            score = (closer, -d, -cheb(nx, ny, ox, oy))
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = (0, 0)
    best_score = None
    for dx, dy, nx, ny in moves:
        d = cheb(nx, ny, ox, oy)
        score = (d, -cheb(nx, ny, sx, sy))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]