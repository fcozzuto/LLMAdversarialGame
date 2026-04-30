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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd = 10**9
        bestm = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    # pick nearest resource (tie-break by coordinates for determinism)
    target = None
    bestt = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < bestt or (d == bestt and (target is None or (rx, ry) < target)):
            bestt, target = d, (rx, ry)
    tx, ty = target

    bestv = None
    bestm = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # prefer getting closer to target, but also discourage allowing opponent to get closer
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # if next step collects resource at nx,ny, make it very desirable
        collect = 1 if (nx, ny) == (tx, ty) else 0

        # secondary: keep away from opponent slightly (deterministic tie-break)
        sep = cheb(nx, ny, ox, oy)

        v = (0 if collect else 1, myd, -sep, opd - myd)
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]