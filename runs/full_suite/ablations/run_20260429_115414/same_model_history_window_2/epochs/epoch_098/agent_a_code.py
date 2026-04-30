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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    # Pick a resource where we are relatively closer than the opponent.
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            dself = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            advantage = dop - dself
            # tie-break deterministically by coordinates
            key = (advantage, -dself, -rx, -ry)
            if best_score is None or key > best_score:
                best_score = key
                best = (rx, ry)
        tx, ty = best
        # Choose move that minimizes our distance to target; secondarily maximizes opponent distance.
        best_mv = None
        best_key = None
        for dx, dy, nx, ny in legal:
            k = (-cheb(nx, ny, tx, ty), cheb(ox, oy, nx, ny), 0 if (nx == tx and ny == ty) else 1, -dx, -dy)
            if best_key is None or k > best_key:
                best_key = k
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    # No resources visible: drift toward center while avoiding traps around obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_mv = None
    best_key = None
    for dx, dy, nx, ny in legal:
        # prefer moving to cells with more free surrounding squares
        free = 0
        for ddx, ddy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            ax, ay = nx + ddx, ny + ddy
            if ok(ax, ay):
                free += 1
        k = (-cheb(nx, ny, cx, cy), free, -dx, -dy)
        if best_key is None or k > best_key:
            best_key = k
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]