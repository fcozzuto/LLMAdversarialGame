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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def best_for_target(tx, ty):
        best = None
        bestv = None
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = manh(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) == (0, 0)):
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda r: (manh(sx, sy, r[0], r[1]), r[0], r[1]))
        return best_for_target(tx, ty)

    dist = manh(sx, sy, ox, oy)
    if dist <= 2:
        best = None
        bestv = None
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = manh(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Deterministic fallback: prefer moves that keep within bounds and follow a simple pattern
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)):
        if ok(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]