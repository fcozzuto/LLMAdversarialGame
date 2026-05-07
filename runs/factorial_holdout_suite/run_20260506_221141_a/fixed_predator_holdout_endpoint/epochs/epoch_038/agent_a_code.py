def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    tx, ty = sx, sy
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(rx + ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    preferred = (sign(tx - sx), sign(ty - sy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = []
    if preferred in moves:
        order.append(preferred)
        for m in moves:
            if m != preferred:
                order.append(m)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            return (-10**9, 0)
        myd = cheb(nx, ny, tx, ty)
        myd0 = cheb(sx, sy, tx, ty)
        # also discourage stepping away from best target
        return (-(myd), myd0 - myd)

    bestm = (0, 0)
    bestk = None
    for dx, dy in order:
        k = cell_score(dx, dy)
        if bestk is None or k > bestk:
            bestk = k
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]