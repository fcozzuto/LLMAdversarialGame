def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    def cd(ax, ay, bx, by):
        a = ax - bx
        b = ay - by
        if a < 0:
            a = -a
        if b < 0:
            b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = -10**18
        for rx, ry in resources:
            myd = cd(nx, ny, rx, ry)
            oppd = cd(ox, oy, rx, ry)
            score = oppd - myd
            if score > my_best:
                my_best = score
        if my_best > best_score:
            best_score = my_best
            best_move = (dx, dy)

    if not valid(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]