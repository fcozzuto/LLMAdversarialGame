def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    obs_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_raw if p is not None)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if res:
        best_t = None
        best_gap = None
        for p in res:
            try:
                rx, ry = p[0], p[1]
            except Exception:
                continue
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            gap = opd - myd
            if best_t is None or gap > best_gap or (gap == best_gap and myd < md(sx, sy, best_t[0], best_t[1])):
                best_t = (rx, ry)
                best_gap = gap
        tx, ty = best_t if best_t is not None else (cx, cy)
        best = None
        for dx, dy, nx, ny in legal:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            gap = opd - myd
            key = (-gap, myd, abs(nx - cx) + abs(ny - cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best = None
    for dx, dy, nx, ny in legal:
        myd = md(nx, ny, cx, cy)
        key = (myd, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]