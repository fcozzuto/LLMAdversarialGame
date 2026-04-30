def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)  # run away from opponent
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    best = None
    bestv = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ndist_opp = cheb(nx, ny, ox, oy)
        # prefer moves that approach a resource we can reach no later than opponent
        v = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # reward reaching resources, penalize giving opponent faster access
            v += (10 - myd) - (opd - myd) * 1.5
            # prefer closer resources more strongly
            v += -0.15 * myd * myd
        # safety term: avoid getting too close while contesting
        v += 0.08 * ndist_opp
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best if best is not None else [0, 0]