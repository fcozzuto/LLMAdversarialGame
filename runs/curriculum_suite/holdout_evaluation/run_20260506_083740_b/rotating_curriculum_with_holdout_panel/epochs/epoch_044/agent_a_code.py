def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def parse_xy(v):
        if v and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    targets = []
    for r in resources:
        xy = parse_xy(r)
        if xy:
            x, y = xy
            if inb(x, y) and (x, y) not in ob:
                targets.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if targets:
        tx, ty = min(targets, key=lambda p: (man(sx, sy, p[0], p[1]), man(ox, oy, p[0], p[1]), p[0], p[1]))
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in ob:
                continue
            v = (man(nx, ny, tx, ty), man(nx, ny, ox, oy), nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    tx, ty = (cx, cy) if resources == [] else (ox, oy)
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue
        v = (man(nx, ny, tx, ty), abs(nx - ox) + abs(ny - oy), nx, ny)
        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]