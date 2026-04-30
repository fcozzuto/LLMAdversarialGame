def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_step(tx, ty):
        best = (10**9, 10**9, 10**9)
        bm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            # prefer approach, then staying away from opponent if equally good
            ov = cheb(nx, ny, ox, oy)
            tup = (v, -ov, 0)  # deterministic tie by scan order
            if tup < best:
                best = tup
                bm = (dx, dy)
        return [bm[0], bm[1]]

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a resource where we are not too far behind; if all are behind, pick the least-worse and head to its "intercept ring"
    scored = []
    for rx, ry in resources:
        myt = cheb(sx, sy, rx, ry)
        opt = cheb(ox, oy, rx, ry)
        diff = myt - opt  # negative means we are sooner
        scored.append((diff, myt, rx, ry))
    scored.sort()
    chosen = scored[0]
    diff, myt, rx, ry = chosen

    if diff <= 0:
        return best_step(rx, ry)

    # Deny/intercept: move to a cell adjacent to that resource that improves our arrival time vs opponent
    ring = []
    for dx, dy in dirs:
        ax, ay = rx + dx, ry + dy
        if ok(ax, ay):
            ring.append((ax, ay))
    if ring:
        ring.sort(key=lambda p: (cheb(sx, sy, p[0], p[1]) - cheb(ox, oy, p[0], p[1]), p[0], p[1]))
        tx, ty = ring[0]
        return best_step(tx, ty)

    return best_step(rx, ry)