def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))
    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy
    if res:
        tx, ty = min(res, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bo = tuple(op) if op and len(op) >= 2 else (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist((nx, ny), (tx, ty))
        opp = dist((nx, ny), (int(bo[0]), int(bo[1])))
        key = (d, -opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]