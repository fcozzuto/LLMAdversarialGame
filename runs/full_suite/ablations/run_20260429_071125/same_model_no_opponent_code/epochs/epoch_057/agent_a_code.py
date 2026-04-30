def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    best_own = None
    best_myd = None
    for r in res:
        myd = cheb((sx, sy), r)
        opd = cheb((ox, oy), r)
        own = opd - myd
        if best_target is None or own > best_own or (own == best_own and myd < best_myd):
            best_target = r
            best_own = own
            best_myd = myd

    target = best_target
    curd = cheb((sx, sy), target)

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb((nx, ny), target)
        dod = cheb((nx, ny), (ox, oy))
        closer = 1 if nd < curd else 0
        score = (-nd * 10.0) + (dod * 0.15) + (closer * 0.35)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move