def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (-(do - ds), ds, cheb(sx, sy, rx, ry))
            # Smaller key[0] means larger (do-ds) advantage; tie by smaller ds.
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)
    else:
        tx, ty = w // 2, h // 2

    best_move = (None, None)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        adv = do2 - ds2  # higher is better
        # Prefer: maximize adv, then minimize self distance to target, then keep move closer to center.
        cx, cy = w / 2 - 0.5, h / 2 - 0.5
        center = cheb(nx, ny, cx, cy)
        key = (-adv, ds2, center, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move[0] is not None else [0, 0]