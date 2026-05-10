def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            rx, ry = int(p[0]), int(p[1])
            res.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not res:
        tx = w - 1 if sx < w // 2 else 0
        ty = h - 1 if sy < h // 2 else 0
        best = (10**9, 10**9, 0, 0)
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, 0 if (nx, ny) == (tx, ty) else 1, abs(nx - ox), abs(ny - oy))
            if k < best:
                best = k
                best_move = [dx, dy]
        return best_move

    best_target = res[0]
    best_key = (-10**18, 10**9, 10**9, 10**9)
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = opd - myd
        k = (-lead, myd, opd, (rx + ry))
        if k < (best_key[0], best_key[1], best_key[2], best_key[3]):
            best_key = (-lead, myd, opd, (rx + ry))
            best_target = (rx, ry)

    tx, ty = best_target
    best = (10**9, 10**9, 10**9, 10**9)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        lead2 = opd2 - myd2
        hit = 0 if (nx, ny) == (tx, ty) else 1
        block = 0 if (abs(nx - ox) + abs(ny - oy) <= 1) else 1
        k = (hit, -lead2, myd2, block)
        if k < best:
            best = k
            best_move = [dx, dy]
    return best_move