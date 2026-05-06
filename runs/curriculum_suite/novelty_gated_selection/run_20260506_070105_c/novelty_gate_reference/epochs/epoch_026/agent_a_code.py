def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    best = None  # (score, do_minus_dm, do, -dm, rx, ry)
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets where opponent is relatively far; if tied, prefer closer to self.
        key = (do - dm, do, -dm)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Evaluate up to 9 moves deterministically; pick best that is in bounds and not blocked.
    moves = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)]
    best_mv = (None, -10**9)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        dm_next = man(nx, ny, tx, ty)
        do_here = man(ox, oy, tx, ty)
        score = (do_here - dm_next, -dm_next, -man(ox, oy, nx, ny), -abs(tx - nx) - abs(ty - ny))
        sc = int(score[0] * 1000 + score[1] * 10 + score[2])
        if best_mv[0] is None or sc > best_mv[1]:
            best_mv = ((mx, my), sc)

    if best_mv[0] is None:
        return [0, 0]
    return [int(best_mv[0][0]), int(best_mv[0][1])]