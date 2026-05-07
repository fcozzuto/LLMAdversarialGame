def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    p = observation.get("self_position") or [0, 0]
    q = observation.get("opponent_position") or [0, 0]
    sx, sy = int(p[0]), int(p[1])
    ox, oy = int(q[0]), int(q[1])

    blocked = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
                res_set.add((x, y))
        except:
            pass

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        for dx, dy, nx, ny in sorted(moves, key=lambda t: (abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy))):
            return [dx, dy]
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for dx, dy, nx, ny in moves:
        if (nx, ny) in res_set:
            myd = 0
            opd = cheb((nx, ny), (ox, oy))
            sc = (-10**6, 0, opd)
        else:
            myd = 10**9
            opd = 10**9
            for rx, ry in resources:
                d1 = cheb((nx, ny), (rx, ry))
                if d1 < myd:
                    myd = d1
                d2 = cheb((ox, oy), (rx, ry))
                if d2 < opd:
                    opd = d2
            sc = (myd - opd, myd, abs(nx - ox) + abs(ny - oy))
        if best is None or sc < best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]