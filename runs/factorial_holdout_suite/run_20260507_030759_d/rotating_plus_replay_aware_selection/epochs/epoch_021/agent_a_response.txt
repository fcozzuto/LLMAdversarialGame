def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in observation["obstacles"] or [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target a resource where we are (or become) the race winner: maximize (d_op - d_self)
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            if ds == 0 and (nx, ny) == (rx, ry):
                score = 10**12
            else:
                do = man(ox, oy, rx, ry)
                # Lead the race strongly; secondarily prefer shorter self distance.
                score = (do - ds) * 100 - ds
            if score > local_best:
                local_best = score
        # Small tie-break: prefer closer to the single best resource we found from this move.
        tie_ds = 10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            if ds < tie_ds:
                tie_ds = ds
        if local_best > best_score or (local_best == best_score and tie_ds < man(sx, sy, sx, sy) + 10):
            best_score = local_best
            best_move = [dx, dy]

    return best_move