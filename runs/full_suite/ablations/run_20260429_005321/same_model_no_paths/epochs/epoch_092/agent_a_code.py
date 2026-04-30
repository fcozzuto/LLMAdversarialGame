def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        bestv = -10**9
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            v = (opd - myd) * 10 - myd
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
        bestm = (0, 0)
        bestd = 10**9
        besttie = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            nd = dist(nx, ny, tx, ty)
            val = (dist(ox, oy, tx, ty) - nd)  # deterministic tie-breaker
            if nd < bestd or (nd == bestd and val > besttie):
                bestd = nd
                besttie = val
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestm = (0, 0)
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist(nx, ny, cx, cy)
        if d < bestd:
            bestd = d
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]