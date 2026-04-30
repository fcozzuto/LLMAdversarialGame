def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources or not valid(sx, sy):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_r = None
    best_sc = -10**9
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        sc = (d2 - d1) * 4 - d1
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        move_sc = (opd - myd) * 4 - myd
        # slight preference to not drift into dead zones: keep closer to board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        move_sc -= dist_center * 0.01
        if move_sc > best:
            best = move_sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]