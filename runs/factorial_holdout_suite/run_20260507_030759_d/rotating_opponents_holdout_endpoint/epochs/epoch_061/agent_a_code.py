def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        res = [(sx, sy)]

    best = (-(10**9), [0, 0])
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        md = 10**9
        for rx, ry in res:
            d = man(nx, ny, rx, ry)
            if d < md:
                md = d
        do = man(nx, ny, ox, oy)
        val = (-md) + (0.15 * do) + (1.0 if md == 0 else 0.0) - (0.2 if do <= 1 else 0.0)
        cand = (dx, dy)
        if val > best[0]:
            best = (val, [dx, dy])
    return best[1]