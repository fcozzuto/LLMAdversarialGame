def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    move_order = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]

    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier (bigger lead), then closer to us.
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # Fallback: head to closest corner that isn't blocked by obstacles.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            myd = cheb(sx, sy, cx, cy)
            key = (-myd, cx, cy)
            if best is None or key > best[0]:
                best = (key, (cx, cy))
        tx, ty = best[1] if best else (sx, sy)
    else:
        tx, ty = best_t

    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_eval = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Race pressure after the move (prefer moves that keep our lead advantage).
        myd_after = nd
        opd_after = cheb(ox, oy, tx, ty)
        lead = opd_after - myd_after
        # Also slightly prefer getting closer to the target.
        eval_key = (lead, -(nd), -(dx * 0 + dy * 0), nx, ny)
        if best_eval is None or eval_key > best_eval:
            best_eval = eval_key
            best_move = [dx, dy]

    return best_move