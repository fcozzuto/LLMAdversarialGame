def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))

    op = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(op[0]), int(op[1])

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if res:
            dmin = min(dist(nx, ny, x, y) for x, y in res)
            target = 0
        else:
            dmin = dist(nx, ny, ox, oy)
            target = 1
        on_border = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            on_border = 1
        key = (target, dmin, on_border, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best