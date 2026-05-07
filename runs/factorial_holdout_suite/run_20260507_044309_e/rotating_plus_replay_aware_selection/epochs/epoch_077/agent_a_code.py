def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource we can "beat" (reach no later than opponent), else closest resource.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Key: prefer winning margin, then faster, then deterministic tie-break.
        win_margin = do - ds
        row_bias = (ry <= oy) - (ry > oy)
        key = (win_margin, -ds, -row_bias, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Also add a small strategic push: if we can't beat any resource, drift toward opponent-blocking by advancing in y.
    if resources:
        can_win = False
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            if cheb(sx, sy, rx, ry) <= cheb(ox, oy, rx, ry):
                can_win = True
                break
        if not can_win:
            ty = max(0, min(h - 1, sy + (1 if sy <= oy else -1)))

    # Pick the move that minimizes our distance to (tx,ty) and (secondarily) maximizes opponent distance.
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Slightly prefer moves that also increase our relative advantage.
        score = (-ds2, do2 - cheb(ox, oy, tx, ty), -((tx - nx) ** 2 + (ty - ny) ** 2))
        # Deterministic tie-break via direction ordering already in moves; keep max score lexicographically.
        if best_m is None or score > best_m[0]:
            best_m = (score, (dx, dy))

    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]