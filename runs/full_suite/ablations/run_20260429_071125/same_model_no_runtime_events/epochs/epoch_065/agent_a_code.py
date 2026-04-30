def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
                res_set.add((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target selection: prefer resources where we are relatively closer than opponent.
    bestT = None
    bestKey = None
    for tx, ty in res:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # maximize advantage (od - md); tie-break by smaller my distance and then by coordinates
        key = (od - md, -md, -tx, -ty)
        if bestKey is None or key > bestKey:
            bestKey = key
            bestT = (tx, ty)
    tx, ty = bestT

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    best = None
    bestScore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Reward collecting immediately.
        collect = 1 if (nx, ny) in res_set else 0
        # Prefer moves that reduce my distance and increase separation from opponent; penalize being near obstacles.
        score = (1000 * collect) + (-10 * myd) + (1.5 * opd) - (0.8 * adj_obst(nx, ny))
        # Deterministic tie-break: prefer smaller dx,dy lexicographically among equal score by sorting key.
        tie = (score, -myd, -opd, -collect, -abs(dx), -abs(dy), -dx, -dy)
        if bestScore is None or tie > bestScore:
            bestScore = tie
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]