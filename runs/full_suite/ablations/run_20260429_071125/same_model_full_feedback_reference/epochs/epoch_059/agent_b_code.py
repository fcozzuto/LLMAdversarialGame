def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = resources[0]
    bestv = -10**9
    for r in resources:
        d_my = cheb((sx, sy), r)
        d_op = cheb((ox, oy), r)
        v = (d_op - d_my) * 5 - d_my
        if v > bestv:
            bestv = v
            best = r

    tx, ty = best
    curd = cheb((sx, sy), (tx, ty))
    bestm = None
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb((nx, ny), (tx, ty))
        if d < bestd or (d == bestd and cheb((ox, oy), (nx, ny)) > cheb((ox, oy), (sx, sy))):
            bestd = d
            bestm = (dx, dy)
    if bestm is not None and bestd <= curd:
        return [bestm[0], bestm[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]