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

    if not ok(sx, sy):
        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    target = None
    if resources:
        target = resources[0]
        bestd = dist((sx, sy), target)
        for r in resources[1:]:
            d = dist((sx, sy), r)
            if d < bestd or (d == bestd and r < target):
                bestd = d
                target = r

    if target is not None:
        tx, ty = target
        best = None
        bestscore = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            nd = dist((nx, ny), (tx, ty))
            score = nd * 100 + (abs(nx - ox) + abs(ny - oy))
            if best is None or score < bestscore:
                bestscore = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # No resources: drift toward opponent cautiously (deterministic).
    best = None
    bestscore = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = (abs(nx - ox) + abs(ny - oy)) * 100 + (abs(nx - sx) + abs(ny - sy))
        if best is None or score < bestscore:
            bestscore = score
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]