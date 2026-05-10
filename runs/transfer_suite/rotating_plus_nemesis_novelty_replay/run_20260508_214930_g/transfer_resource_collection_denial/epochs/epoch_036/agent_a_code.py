def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_sc = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        lead = oppd - myd  # positive => we arrive no later than opponent
        center = abs(rx - cx) + abs(ry - cy)
        sc = lead * 60 - myd - center * 0.2
        key = (sc, -myd, center, -rx, -ry)
        if best_sc is None or sc > best_sc or (sc == best_sc and key < best[0]):
            best_sc = sc
            best = (key, (rx, ry))

    tx, ty = best[1]

    moves = [
        [0, 0], [1, 0], [0, 1], [-1, 0], [0, -1],
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ]

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            sc = 10**9
        else:
            nd = cheb(nx, ny, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            my_after = cheb(nx, ny, tx, ty)
            # slight bonus for improving time lead vs opponent
            sc = nd - (oppd - my_after) * 0.05
        if best_score is None or sc < best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move