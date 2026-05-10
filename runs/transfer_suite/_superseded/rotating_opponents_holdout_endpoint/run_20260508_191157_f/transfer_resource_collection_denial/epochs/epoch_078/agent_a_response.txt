def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: (md(sx, sy, c[0], c[1]), c[0] * 9 + c[1]))
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                if md(nx, ny, tx, ty) < md(sx, sy, best[0] + sx, best[1] + sy):
                    best = [dx, dy]
        return [int(best[0]), int(best[1])]

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Prefer resources we are closer to; also prefer closer targets overall
        key = (-(myd <= opd), myd - opd, myd, rx * 9 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    cur_best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        # If stepping closer to our chosen target, prioritize; tie-break by avoiding squares where opponent is likely closer
        opd = md(ox, oy, tx, ty)
        key = (myd, abs(myd - opd), nx * 9 + ny)
        if cur_best is None or key < cur_best:
            cur_best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]