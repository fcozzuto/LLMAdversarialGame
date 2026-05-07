def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Pick a resource where we are ahead; otherwise pick the best "next contest" target.
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            advantage = do - ds  # positive => we are closer
            key = (0 if advantage > 0 else 1, -advantage, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Primary: reduce distance to target. Secondary: avoid moving into being easily outpaced.
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (ds, 0 if ds < do else 1, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if legal(sx + best_move[0], sy + best_move[1]):
        return [best_move[0], best_move[1]]
    return [0, 0]