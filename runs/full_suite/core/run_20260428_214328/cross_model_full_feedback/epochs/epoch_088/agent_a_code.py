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

    res = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                res.append((x, y))
                seen.add((x, y))

    if res:
        tx, ty = res[0]
        bd = None
        for x, y in res:
            d = abs(sx - x) + abs(sy - y)
            if bd is None or d < bd or (d == bd and (y, x) < (ty, tx)):
                bd = d
                tx, ty = x, y
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

    best = None
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            d = dist(nx, ny, tx, ty)
            if best is None or d < best or (d == best and (dy, dx) < (bestm[1], bestm[0])):
                best = d
                bestm = (dx, dy)

    return [bestm[0], bestm[1]]