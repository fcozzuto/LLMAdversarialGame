def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    tx, ty = ox, oy
    if resources:
        best = None
        for x, y in resources:
            d = abs(sx - x)
            e = abs(sy - y)
            dist = d if d >= e else e
            if best is None or dist < best[0]:
                best = (dist, x, y)
        tx, ty = best[1], best[2]

    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    candidates = []
    for adx in (-1, 0, 1):
        for ady in (-1, 0, 1):
            nx, ny = sx + adx, sy + ady
            if ok(nx, ny):
                candidates.append((adx, ady))
    if (dx, dy) in candidates:
        return [dx, dy]

    best = None
    for adx, ady in candidates:
        nx, ny = sx + adx, sy + ady
        dist = abs(nx - tx)
        dist2 = abs(ny - ty)
        dist = dist if dist >= dist2 else dist2
        score = dist
        if best is None or score < best[0]:
            best = (score, adx, ady)
    return [best[1], best[2]] if best else [0, 0]