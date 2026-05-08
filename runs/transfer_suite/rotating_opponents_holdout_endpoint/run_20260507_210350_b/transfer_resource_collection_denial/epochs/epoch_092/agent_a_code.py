def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy

    def blocked(adj):
        x, y = adj
        if not (0 <= x < w and 0 <= y < h):
            return True
        return (x, y) in obstacles

    def open_score(x, y):
        # count free 8-neighborhood cells (excluding obstacles)
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not blocked((nx, ny)):
                    s += 1
        return s

    best_t = None
    best_key = None
    for tx, ty in res:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        key = (opd - myd, myd, -open_score(tx, ty), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If diagonal is blocked, try axis moves deterministically.
    nx, ny = sx + dx, sy + dy
    if dx != 0 and dy != 0 and blocked((nx, ny)):
        if not blocked((sx + dx, sy)):
            return [dx, 0]
        if not blocked((sx, sy + dy)):
            return [0, dy]
        return [0, 0]
    if (dx != 0 or dy != 0) and blocked((nx, ny)):
        # Prefer x move first, then y, else stay.
        if not blocked((sx + dx, sy)):
            return [dx, 0]
        if not blocked((sx, sy + dy)):
            return [0, dy]
        return [0, 0]
    return [dx, dy]