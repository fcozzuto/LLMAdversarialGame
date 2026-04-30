def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # drift toward middle
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Identify a "most swingable" resource from current state
    best_cur = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        swing = od - sd
        # prefer higher swing, then closer distance
        key = (swing, -(sd), -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cur = (rx, ry)

    tx, ty = best_cur
    # If we can already secure a resource this step, try to step onto it
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Evaluate each move by the best swing we can generate next turn
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # compute our best immediate swing from next position
        local_best = -10**9
        for rx, ry in resources:
            sd2 = md(nx, ny, rx, ry)
            od2 = md(ox, oy, rx, ry)
            swing2 = od2 - sd2
            # also encourage reducing our distance to our chosen target
            d_target = md(nx, ny, tx, ty)
            val = (swing2 * 20) - sd2 + (10 - d_target)
            if val > local_best:
                local_best = val

        # small tie-breaker: move toward chosen target to commit
        toward = -(abs(nx - tx) + abs(ny - ty))
        val2 = local_best + toward * 0.1

        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]