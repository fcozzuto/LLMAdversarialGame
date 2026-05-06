def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    if not targets:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
        if legal(sx, sy):
            return [0, 0]
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestd = None
    bests = None
    for tx, ty in targets:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), (tx, ty))
            sd = dist((sx, sy), (tx, ty))
            s = 0
            if d < sd:
                s += 10
            if ox == nx and oy == ny:
                s -= 100
            s += -d
            if best is None or s > bests or (s == bests and d < bestd):
                best = (dx, dy)
                bestd = d
                bests = s

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]