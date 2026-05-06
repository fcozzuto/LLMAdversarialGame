def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def best_target():
        best = None
        best_k = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            k = (do - ds, ds, rx, ry)
            if best is None or k < best_k:
                best = (rx, ry)
                best_k = k
        return best

    tx, ty = best_target()
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        score = (no - ns, -ns, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move