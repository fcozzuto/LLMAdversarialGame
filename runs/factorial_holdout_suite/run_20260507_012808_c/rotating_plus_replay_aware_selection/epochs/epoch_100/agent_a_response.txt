def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (dx, dy) < tuple(best)):
                    bestd = d
                    best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    best_move = [0, 0]
    best_val = -10**18
    best_ourd = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best = -10**18
        local_our = 10**9
        for rx, ry in res:
            ourd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            val = (opd - ourd) * 10 - ourd
            if val > local_best or (val == local_best and ourd < local_our):
                local_best = val
                local_our = ourd
        if local_best > best_val or (local_best == best_val and (local_our < best_ourd or (local_our == best_ourd and (dx, dy) < tuple(best_move)))):
            best_val = local_best
            best_ourd = local_our
            best_move = [dx, dy]

    return best_move