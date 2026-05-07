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

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we arrive earlier
            # maximize adv, then be closer, then harder for opponent
            key = (-adv, ds, do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is not None:
            tx, ty = best[1]
        else:
            tx, ty = w // 2, h // 2
    else:
        tx, ty = w // 2, h // 2

    # Choose move that reduces our distance to the target; tie-break by increasing reach advantage.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid_moves:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv_after = opd - myd
        key = (myd, -adv_after, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]