def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    w = observation["grid_width"]
    h = observation["grid_height"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_free(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def best_value(myx, myy, opx, opy):
        best = None
        for rx, ry in resources:
            myd = cheb(myx, myy, rx, ry)
            opd = cheb(opx, opy, rx, ry)
            v = myd - 0.9 * opd  # prefer resources where opponent is relatively far
            if best is None or v < best:
                best = v
        return best

    cur_val = best_value(sx, sy, ox, oy)

    best_move = [0, 0]
    best_val = cur_val
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        v = best_value(nx, ny, ox, oy)
        if v < best_val:
            best_val = v
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # break ties by moving toward the closest resource (still obstacle-safe)
        target = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))
        tx, ty = target
        cand = [0, 0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for ddx, ddy in moves:
            if ddx == dx and ddy == dy:
                nx, ny = sx + ddx, sy + ddy
                if cell_free(nx, ny):
                    cand = [ddx, ddy]
                break
        return cand

    return best_move