def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer resources where we are (or will be) relatively closer
            val = (myd - 0.65 * opd)
            if best is None or val < best:
                best = val
                target = (rx, ry)

    best_move = moves[0]
    best_score = None
    for dx, dy, nx, ny in moves:
        if target is not None:
            rx, ry = target
            myd_next = cheb(nx, ny, rx, ry)
            myd_now = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # encourage getting closer to target, discourage letting opponent be closer
            score = (-(myd_next) + 0.12 * myd_now - 0.08 * max(0, opd - myd_next))
        else:
            # no resources visible: drift toward center while not getting too close to opponent
            score = (-cheb(nx, ny, cx, cy) + 0.06 * cheb(nx, ny, ox, oy))
        # deterministic tie-breakers
        score += -0.001 * (abs(nx - sx) + abs(ny - sy))
        score += 0.0001 * (nx * 0.3 + ny * 0.7)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]