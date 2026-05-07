def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            res.append((r[0], r[1]))
        except Exception:
            pass

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    target = (w - 1, h - 1)
    if res:
        tx, ty = min(res, key=lambda p: man(sx, sy, p[0], p[1]))
        target = (tx, ty)

    best = None
    best_sc = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if man(nx, ny, target[0], target[1]) == 0:
            sc = 10**9
        else:
            sc = -man(nx, ny, target[0], target[1])
        if res:
            nearest = min(res, key=lambda p: man(nx, ny, p[0], p[1]))
            myd = man(nx, ny, nearest[0], nearest[1])
            opd = man(ox, oy, nearest[0], nearest[1])
            sc += 2 * (opd - myd)
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]