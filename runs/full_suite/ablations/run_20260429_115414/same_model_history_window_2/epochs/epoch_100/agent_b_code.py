def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = [(dx, dy, sx + dx, sy + dy) for dx, dy in moves if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    best = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, rx, ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    tx, ty = target if target is not None else (w // 2, h // 2)

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        ds1 = md(nx, ny, tx, ty)
        do = md(ox, oy, tx, ty)
        score = (do - ds1, -ds1, -md(nx, ny, ox, oy), dx * 0 + dy * 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]