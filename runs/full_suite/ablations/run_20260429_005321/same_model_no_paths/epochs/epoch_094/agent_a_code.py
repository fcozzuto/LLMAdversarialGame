def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))

    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            # lower is better: (closest resource distance) with contest/proximity pressure
            dmin = None
            dmin_opp = None
            tie = []
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
                d2 = cheb(ox, oy, rx, ry)
                if dmin_opp is None or d2 < dmin_opp:
                    dmin_opp = d2
                if d == 1:  # strong: immediate pickup next step
                    tie.append((rx, ry))
            # if we can grab immediately, prioritize it strongly
            score = dmin * 100 + cheb(nx, ny, ox, oy) - (0 if dmin_opp is None else dmin_opp)
            if len(tie) > 0:
                score = -1000 + len(tie)
            cand = (score, dmin if dmin is not None else 0, (nx, ny), (dx, dy))
            if bestv is None or cand < (bestv, best) if False else cand:
                bestv = cand[0]
                best = (dx, dy)
                bestkey = cand
            elif cand < bestkey:
                best = (dx, dy)
                bestkey = cand
        return [int(best[0]), int(best[1])]

    # No resources: move toward center while mildly keeping distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestkey = None
    for dx, dy, nx, ny in moves:
        dcenter = cheb(nx, ny, cx, cy)
        dop = cheb(nx, ny, ox, oy)
        cand = (dcenter, -dop, (nx, ny), (dx, dy))
        if bestkey is None or cand < bestkey:
            bestkey = cand
            best = (dx, dy)
    return [int(best[0]), int(best[1])]