def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist_time(a, b):
        # diagonal-allowed move time: Chebyshev
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for r in res:
        st = dist_time((sx, sy), r)
        ot = dist_time((ox, oy), r)
        # Prefer resources we can get no later than opponent; break ties by bigger advantage, then nearer.
        key = (0, 0, 0)
        if st <= ot:
            key = (1, ot - st, -(st))
        else:
            key = (0, -(st), 0)
        if best is None or key > best_key:
            best, best_key = r, key

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = [(dx, dy)]
    # If blocked, try alternate step(s) that still reduce distance.
    if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obs:
        return [dx, dy]

    def cheb(a, b):
        d1 = a[0] - b[0]
        d2 = a[1] - b[1]
        if d1 < 0: d1 = -d1
        if d2 < 0: d2 = -d2
        return d1 if d1 > d2 else d2

    curd = cheb((sx, sy), (tx, ty))
    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_step = (0, 0)
    best_c = -1
    for mx, my in steps:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb((nx, ny), (tx, ty))
        gain = curd - nd
        # Deterministic tie-break: maximize gain, then prefer diagonal, then lexicographic.
        diag = 1 if mx != 0 and my != 0 else 0
        score = (gain, diag, -(mx * 10 + my))
        if score > best_c:
            best_c = score
            best_step = (mx, my)

    return [int(best_step[0]), int(best_step[1])]