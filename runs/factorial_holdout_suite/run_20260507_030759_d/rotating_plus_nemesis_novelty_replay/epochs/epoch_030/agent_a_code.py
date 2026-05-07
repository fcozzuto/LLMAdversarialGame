def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mdist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def obst_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sp_next = (nx, ny)
        pen = obst_pen(nx, ny)
        if pen >= 10**8:
            continue
        score = -pen * 5
        for rx, ry in res:
            sd = mdist(nx, ny, rx, ry)
            od = mdist(ox, oy, rx, ry)
            if (nx, ny) == (rx, ry):
                score += 2000
            if sd < od:
                score += 120 - sd
            elif sd == od:
                score += 10 - sd
            else:
                score -= 40 + sd
        if score > best_score or (score == best_score and (best is None or (abs(nx - ox) + abs(ny - oy), -nx, -ny) < (abs(best[0] - ox) + abs(best[1] - oy), -best[0], -best[1]))):
            best_score = score
            best = (nx, ny, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]