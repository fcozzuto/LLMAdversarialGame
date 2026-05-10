def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

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

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for r in res:
        st = cheb((sx, sy), r)
        ot = cheb((ox, oy), r)
        # Prefer resources we can reach no later than opponent; otherwise minimize the delay
        if st <= ot:
            key = (0, -(ot - st), st, r[0], r[1])
        else:
            key = (1, (st - ot), st, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    safe = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            safe.append((dx, dy, nx, ny))
    if not safe:
        return [0, 0]

    bestm = None
    bestmk = None
    for dx, dy, nx, ny in safe:
        d = cheb((nx, ny), (tx, ty))
        # Bonus if stepping onto a resource
        on_res = 1 if (nx, ny) in set(res) else 0
        # Tie-break: keep opponent farther from target relative to us
        my_t = d
        op_t = cheb((ox, oy), (tx, ty))
        key = (-on_res, d, (my_t - op_t), nx, ny, dx, dy)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = [dx, dy]
    return bestm