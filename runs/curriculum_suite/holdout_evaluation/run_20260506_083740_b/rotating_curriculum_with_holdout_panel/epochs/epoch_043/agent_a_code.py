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
            try:
                ob.add((int(p[0]), int(p[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestd = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = md(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    res = []
    for r in resources:
        if r and len(r) >= 2:
            try:
                res.append((int(r[0]), int(r[1])))
            except:
                pass
    if not res:
        return [0, 0]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = -10**18
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            score = d_opp - d_self  # higher means we are closer than opponent
            if score > v:
                v = score
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]