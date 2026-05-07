def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer: maximize advantage (we closer), then minimize our distance, then minimize opponent distance
            key = (od - sd, -sd, -od)
            if move_best is None or key > move_best:
                move_best = key

        if move_best is None:
            continue
        if best is None or move_best > best:
            best = move_best
            best_move = [dx, dy]

    return best_move