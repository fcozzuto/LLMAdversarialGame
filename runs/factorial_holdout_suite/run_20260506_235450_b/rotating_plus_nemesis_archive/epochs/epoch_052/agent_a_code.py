def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer positions that can win resources (closer than opponent), then just minimize opponent advantage and our distance.
        local_best = None
        for rx, ry in resources:
            d_us = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # If we can arrive no later, strongly prefer; otherwise try to minimize how much we fall behind.
            win_bias = 0 if d_us <= d_op else (d_us - d_op + 4)
            val = (win_bias, d_us, d_op, rx, ry)
            if local_best is None or val < local_best:
                local_best = val
        if local_best is None:
            continue
        if best is None or local_best < best:
            best = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]