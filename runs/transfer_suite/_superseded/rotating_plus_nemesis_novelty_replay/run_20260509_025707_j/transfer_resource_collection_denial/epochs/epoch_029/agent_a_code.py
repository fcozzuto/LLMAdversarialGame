def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    bestd = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not ok(rx, ry):
            continue
        d = md(sx, sy, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)

    best_move = (0, 0)
    if target is not None:
        tx, ty = target
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (md(nx, ny, tx, ty), md(ox, oy, nx, ny), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (-md(nx, ny, ox, oy), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]