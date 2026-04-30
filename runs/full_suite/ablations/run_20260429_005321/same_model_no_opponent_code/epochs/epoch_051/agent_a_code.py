def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        best = None
        for r in resources:
            d = cheb((sx, sy), r)
            o = cheb((ox, oy), r)
            score = d - (0.5 if d <= o else -0.5)  # prefer resources at least as near as opponent
            tup = (score, o, r[0], r[1])
            if best is None or tup < best:
                best = tup
                target = r

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target is not None:
            val = cheb((nx, ny), target)
            # slight bias toward keeping away from opponent while collecting target
            val = val * 10 + (10 - cheb((nx, ny), (ox, oy)))
        else:
            # no resources known: drift toward center while avoiding opponent a bit
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = cheb((nx, ny), (cx, cy)) * 10 - cheb((nx, ny), (ox, oy))
        cand = (val, nx, ny, dx, dy)
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]