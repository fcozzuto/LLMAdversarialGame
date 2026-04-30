def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_val, best_move = -10**18, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_near = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = cheb(nx, ny, ox, oy)
            val = (-d_near, d_opp)
            if val > (best_val, best_move):
                best_val = val[0]
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best, best_move = -10**18, (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = cheb(nx, ny, cx, cy) - 2 * cheb(nx, ny, ox, oy)
        if v > best:
            best, best_move = v, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]