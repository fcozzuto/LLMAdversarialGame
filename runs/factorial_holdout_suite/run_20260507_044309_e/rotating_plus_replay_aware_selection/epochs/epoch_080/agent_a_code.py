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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def pick_target(px, py):
        if not resources:
            return (w // 2, h // 2)
        best_key = None
        best_pos = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # we prefer resources where we can arrive earlier
            # slight deterministic bias: prefer upper-left-ish to reduce ties
            key = (margin, -ds, ry, rx)
            if best_key is None or key > best_key:
                best_key = key
                best_pos = (rx, ry)
        return best_pos if best_pos is not None else (w // 2, h // 2)

    tx, ty = pick_target(sx, sy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(ox, oy, tx, ty)  # opponent unchanged this turn
        margin1 = do1 - ds1
        # maximize immediate capture likelihood and advantage; tie-break deterministically
        score = (margin1, -ds1, ny, nx)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]