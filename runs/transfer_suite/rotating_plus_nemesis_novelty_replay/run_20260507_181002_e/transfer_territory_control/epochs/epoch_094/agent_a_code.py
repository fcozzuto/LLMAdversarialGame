def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed:
        unclaimed = set(resources) if resources else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = None
    if unclaimed:
        targets = unclaimed
    elif resources:
        targets = resources

    tx, ty = ox, oy
    if targets:
        bestd = 10**18
        for x, y in targets:
            d = md(sx, sy, x, y)
            if d < bestd:
                bestd = d
                tx, ty = x, y

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    best = None
    bestv = -10**18
    cx, cy = w // 2, h // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (obstacles and (nx, ny) in obstacles):
            continue
        v = 0
        v += -md(nx, ny, tx, ty) * 10
        v += md(nx, ny, ox, oy)
        v += -md(nx, ny, cx, cy) * 0.01
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best