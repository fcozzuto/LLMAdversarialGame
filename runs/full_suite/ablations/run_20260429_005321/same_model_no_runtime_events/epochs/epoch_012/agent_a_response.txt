def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obstacles:
                resources.append(t)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in legal:
            myd = cheb(nx, ny, cx, cy)
            opd = cheb(ox, oy, cx, cy)
            key = (-(myd + (1 if (nx, ny) == (sx, sy) else 0)), -(opd - myd))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in legal:
        my_best = 10**9
        op_best_at_my = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if myd < my_best:
                my_best = myd
            opd = cheb(ox, oy, rx, ry)
            if myd <= my_best and opd < op_best_at_my:
                op_best_at_my = opd
        # Better if we can get closer to some resource than opponent can.
        # Use strongest "lead" we can claim, and then prefer smaller my_best.
        lead = op_best_at_my - my_best
        # Extra tie-break: reduce opponent's best distance to our chosen target region by also
        # penalizing moves that make us worse off across all resources.
        my_all = 0
        op_all = 0
        for rx, ry in resources:
            my_all += cheb(nx, ny, rx, ry)
            op_all += cheb(ox, oy, rx, ry)
        key = (lead, -(my_best), -(my_all - op_all // max(1, len(resources))), -(abs((nx - ox)) + abs((ny - oy))))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]