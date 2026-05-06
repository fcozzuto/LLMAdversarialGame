def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a move that maximizes "grab advantage": (opp_dist - my_dist) to best target.
    # If no clear advantage, prefer shortest my_dist to avoid falling behind.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_best = None
        for rx, ry in res:
            myd = d((nx, ny), (rx, ry))
            opd = d((ox, oy), (rx, ry))
            # Large key favors targets where we are closer than opponent; ties break by myd.
            key = (opd - myd, -myd, -rx, -ry)
            if my_best is None or key > my_best:
                my_best = key
        overall = (my_best[0], my_best[1])
        if best_key is None or overall > best_key:
            best_key = overall
            best_move = [dx, dy]

    return best_move if best_move in ([m[0], m[1]] for m in moves) else [0, 0]