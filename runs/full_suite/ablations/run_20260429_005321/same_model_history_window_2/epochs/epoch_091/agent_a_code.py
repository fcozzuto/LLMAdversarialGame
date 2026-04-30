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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Go toward opponent-side center-ish to stay active.
        tx, ty = (w - 1, h - 1)
        bestd = 10**9
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    bestv = -10**18
    bestm = (0, 0)
    # Deterministic tie-break by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        myd_best = 10**9
        val_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if myd < myd_best:
                myd_best = myd
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            # Encourage taking when we have advantage; otherwise compete minimally.
            v = adv * 20 - myd * 2
            # If opponent can't reach it immediately but we can, spike.
            if adv >= 1:
                v += 50
            val_best = v if v > val_best else val_best

        # Mild preference for reducing direct distance to best reachable resource.
        v = val_best - myd_best * 0.5
        if v > bestv:
            bestv, bestm = v, (dx, dy)
        elif v == bestv and (dx, dy) < bestm:
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]