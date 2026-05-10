def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if res:
        tx, ty = res[0]
        bestd = man(sx, sy, tx, ty)
        for x, y in res[1:]:
            d = man(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                tx, ty, bestd = x, y, d
        target_score = (bestd, tx, ty)
    else:
        tx, ty = ox, oy
        bestd = man(sx, sy, ox, oy)
        target_score = (bestd, tx, ty)

    best = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        opp = man(nx, ny, ox, oy)
        if res:
            score = (d, -opp, ddx, ddy)
        else:
            score = (d, -opp, ddx, ddy)
        if best is None or score < best:
            best = score
            best_move = [ddx, ddy]

    if best is None:
        return [0, 0]
    return best_move