def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if resources:
        sxr, syr = sx, sy
        best = None
        bestd = 10**9
        for r in resources:
            d = cheb((sxr, syr), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None:
            tx, ty = best
        else:
            tx, ty = ox, oy
    else:
        tx, ty = ox, oy

    def dist(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    bestm = None
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        if d < bestd or (d == bestd and ((ny, nx) < (bestm[1], bestm[0]) if bestm else False)):
            bestd = d
            bestm = (dx, dy)

    if bestm is None:
        # fallback to stay
        return [0, 0]
    return [bestm[0], bestm[1]]