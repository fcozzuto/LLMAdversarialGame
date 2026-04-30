def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -(man(nx, ny, tx, ty)) + 0.3 * man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_r = None
    bestd = 10**18
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except Exception:
            continue
        d = man(sx, sy, rx, ry)
        if d < bestd:
            bestd = d
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        toward = -man(nx, ny, rx, ry)
        avoid = 0.25 * man(nx, ny, ox, oy)
        onres = 2.0 if (nx, ny) == (rx, ry) else 0.0
        v = toward + avoid + onres
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best