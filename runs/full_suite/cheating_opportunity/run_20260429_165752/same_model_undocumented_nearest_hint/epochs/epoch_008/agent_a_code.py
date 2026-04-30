def choose_move(observation):
    W = observation.get("grid_width", 8) or 8
    H = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best = None
    bestk = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if res:
            dmin = 10**9
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
        else:
            dmin = 0
        do = md(nx, ny, ox, oy)
        k = (-dmin, do, 0 if (dx, dy) == (0, 0) else 1)
        if bestk is None or k > bestk:
            bestk = k
            best = (dx, dy)
    return [int(best[0]), int(best[1])]