def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            dirs.append((dx, dy))
    if not dirs:
        return [0, 0]

    def man(a, b, c, d):
        v = a - c
        if v < 0: v = -v
        t = b - d
        if t < 0: t = -t
        return v + t

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        score = 0
        if (nx, ny) in res:
            score += 100000
        if res:
            mdmin = 10**9
            for rx, ry in res:
                d = man(nx, ny, rx, ry)
                if d < mdmin:
                    mdmin = d
            score -= mdmin * 10
        score += man(nx, ny, ox, oy) * 2
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]