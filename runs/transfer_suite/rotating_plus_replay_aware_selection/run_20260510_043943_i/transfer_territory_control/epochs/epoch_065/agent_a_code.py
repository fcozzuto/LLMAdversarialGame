def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                targets.append((x, y))

    if targets:
        best = None
        bestd = None
        for x, y in targets:
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd:
                bestd = d
                best = (x, y)
            elif d == bestd and (x, y) < best:
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    def score(dx, dy):
        nx, ny = sx + dx, sy + dy
        toward = -((abs(tx - nx) + abs(ty - ny)) * 10)
        away = (abs(nx - ox) + abs(ny - oy)) * 3
        return toward + away

    bestm = None
    bests = None
    for dx, dy in candidates:
        s = score(dx, dy)
        if bests is None or s > bests or (s == bests and (dx, dy) < bestm):
            bests = s
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]