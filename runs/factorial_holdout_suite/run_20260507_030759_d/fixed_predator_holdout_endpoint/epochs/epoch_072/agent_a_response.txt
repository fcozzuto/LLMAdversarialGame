def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_score = None  # (margin, -self_dist, self_dist, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local = None
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive => we are closer than opponent
            cand = (margin, -ds, ds, rx, ry)
            if local is None or cand > local:
                local = cand
        if local is None:
            continue
        if best_score is None or local > best_score:
            best_score = local
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]