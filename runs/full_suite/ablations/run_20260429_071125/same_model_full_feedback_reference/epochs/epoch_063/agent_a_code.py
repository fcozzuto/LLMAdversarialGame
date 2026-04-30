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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        target = resources[0]
        best = cheb(sx, sy, target[0], target[1])
        for r in resources[1:]:
            d = cheb(sx, sy, r[0], r[1])
            if d < best or (d == best and (r[0] < target[0] or (r[0] == target[0] and r[1] < target[1]))):
                best = d
                target = r
        tx, ty = target
        bestm = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), (nx, ny))
            if bestv is None or v < bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # No resources known: step away from opponent, tie-break toward center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    bestm = None
    bestv = None
    for dx, dy, nx, ny in moves:
        v = (-cheb(nx, ny, ox, oy), (abs(nx - cx) + abs(ny - cy)), (nx, ny))
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]