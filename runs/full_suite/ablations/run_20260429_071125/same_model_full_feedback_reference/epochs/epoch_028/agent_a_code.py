def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            dop = abs(nx - ox) + abs(ny - oy)
            score = dres * 1000 - dop
            cand = (score, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is not None:
            return [best[1], best[2]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - cx) + abs(ny - cy)
        cand = (d, dx, dy)
        if best is None or cand < best:
            best = cand
    if best is not None:
        return [best[1], best[2]]
    return [0, 0]