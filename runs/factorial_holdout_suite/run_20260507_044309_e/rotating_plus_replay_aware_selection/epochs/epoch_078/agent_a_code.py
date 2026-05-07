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

    def blocked(x, y):
        return x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles

    def legal_step(dx, dy):
        nx, ny = sx + dx, sy + dy
        return (not blocked(nx, ny))

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best_key = None
        best = (w // 2, h // 2)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            win = do - ds  # positive means we arrive no later than opponent
            row_bias = (ry <= oy) - (ry > oy)
            key = (win, -ds, row_bias, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    cur_d = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best = None
    for dx, dy in moves:
        if not legal_step(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        nd = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer steps that reduce distance; tie-break by improving relative arrival vs opponent and determinism.
        step_key = (-nd, -(do - nd), -abs(nx - tx), nx, ny)
        if best is None or step_key > best:
            best = step_key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move