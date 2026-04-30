def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = resources[0]
        best = cheb(sx, sy, tx, ty)
        for x, y in resources[1:]:
            v = cheb(sx, sy, x, y)
            if v < best:
                best = v
                tx, ty = x, y
    else:
        tx, ty = w // 2, h // 2

    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if ok(nx, ny):
        return [dx, dy]

    bestm = (0, 0)
    bestv = 10**9
    for mx, my in moves:
        x, y = sx + mx, sy + my
        if ok(x, y):
            v = cheb(x, y, tx, ty)
            if v < bestv:
                bestv = v
                bestm = (mx, my)
    return [bestm[0], bestm[1]]