def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        w, h = 8, 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
        except Exception:
            continue
        obs.add((int(x), int(y)))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def free(x, y): 
        return inb(x, y) and (x, y) not in obs

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        try:
            x, y = p
            res.append((int(x), int(y)))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = None

    if res:
        targets = [r for r in res if free(r[0], r[1])]
        if not targets:
            targets = res
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dmin = min(cheb(nx, ny, tx, ty) for (tx, ty) in targets)
            do = cheb(nx, ny, ox, oy)
            sc = -dmin - 0.05 * do
            if best_sc is None or sc > best_sc:
                best_sc, best = sc, [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            do = cheb(nx, ny, ox, oy)
            dc = cheb(nx, ny, w // 2, h // 2)
            sc = do - 0.01 * dc
            if best_sc is None or sc > best_sc:
                best_sc, best = sc, [dx, dy]

    return best if best is not None else [0, 0]