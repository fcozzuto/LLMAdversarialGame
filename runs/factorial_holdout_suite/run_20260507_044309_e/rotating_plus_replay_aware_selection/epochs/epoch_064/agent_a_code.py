def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        win = 0 if ds < do else 1  # prefer resources we can beat
        adv = do - ds  # larger is better when win=0
        key = (win, -adv, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    tx, ty = (w // 2, h // 2) if best is None else (best[1], best[2])

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)  # keep some distance from denier; deterministic bias
        k = (d, od * 0, -od, dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]