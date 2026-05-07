def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_resource(px, py):
        if not resources:
            return (w // 2, h // 2)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Favor resources we can beat (do-ds), then shorter travel, then deterministic preference.
            # Also slightly prefer resources that are "above" us relative to opponent's row sweeping.
            row_bias = (ry <= oy) - (ry > oy)
            key = (do - ds, -ds, -row_bias, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        if best is None:
            return (w // 2, h // 2)
        return best[1]

    def step_score(px, py):
        tx, ty = best_resource(px, py)
        ds = cheb(px, py, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # After moving, prefer states where we are closer AND the opponent is further from the same target.
        return (do - ds, -ds, -abs(tx - px), -abs(ty - py))

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = step_score(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]