def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        best = None
        for x, y in resources:
            sdist = d2(sx, sy, x, y)
            odist = d2(ox, oy, x, y)
            cand = (sdist, odist, x, y)
            if best is None or cand < best:
                best = cand
                target = (x, y)

        tx, ty = target
        bestm = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            m = (d2(nx, ny, tx, ty), d2(nx, ny, ox, oy), dx, dy)
            if bestm is None or m < bestm:
                bestm = m
        if bestm is not None:
            return [bestm[2], bestm[3]]

    bestm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        m = (-d2(nx, ny, ox, oy), d2(nx, ny, sx, sy), dx, dy)
        if bestm is None or m < bestm:
            bestm = m
    if bestm is not None:
        return [bestm[2], bestm[3]]

    return [0, 0]