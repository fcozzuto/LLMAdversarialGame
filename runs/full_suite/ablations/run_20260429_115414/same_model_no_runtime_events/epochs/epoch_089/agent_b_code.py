def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (0, 0, -10**9)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny):
                continue
            sc = cheb(nx, ny, ox, oy)  # maximize separation
            if sc > best[2]:
                best = (mx, my, sc)
        return [best[0], best[1]]

    tx, ty = resources[0]
    bestd = cheb(sx, sy, tx, ty)
    for rx, ry in resources[1:]:
        d = cheb(sx, sy, rx, ry)
        if d < bestd or (d == bestd and (rx, ry) < (tx, ty)):
            bestd, tx, ty = d, rx, ry

    # Candidate scoring: prioritize reaching target, while discouraging moving toward opponent and avoiding dead-ends.
    bestm = (0, 0)
    bests = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        dT = cheb(nx, ny, tx, ty)
        dO = cheb(nx, ny, ox, oy)
        adj = 1 if cheb(nx, ny, tx, ty) <= 1 else 0
        # small "pressure" term: prefer positions with more onward free cells
        free = 0
        for sx2, sy2 in moves:
            ax, ay = nx + sx2, ny + sy2
            if inb(ax, ay):
                free += 1
        sc = (-dT * 10) + (dO * 0.6) + (adj * 6) + (free * 0.15)
        # deterministic tie-break: lexicographic on move deltas
        if sc > bests or (sc == bests and (mx, my) < bestm):
            bests, bestm = sc, (mx, my)
    return [int(bestm[0]), int(bestm[1])]