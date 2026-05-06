def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            margin = opd - myd
            key = (margin, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (None, None, None, None)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        myd = md(nx, ny, tx, ty)
        opd_after = md(nx, ny, ox, oy)
        oppd_target = md(ox, oy, tx, ty)
        myd_now = md(sx, sy, tx, ty)
        improvement = (myd_now - myd)  # prefer getting closer
        margin_after = oppd_target - myd

        # score: maximize margin and improvement, then maximize distance from opponent, then stay near target
        score = (margin_after, improvement, opd_after, -myd, -abs(nx - sx) - abs(ny - sy), -nx - 10 * ny)
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy, nx, ny)

    return [int(best_mv[0]), int(best_mv[1])]