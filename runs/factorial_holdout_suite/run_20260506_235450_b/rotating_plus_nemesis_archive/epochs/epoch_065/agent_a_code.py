def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_int(v):
        try:
            return int(v)
        except:
            return 0

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is None:
            continue
        try:
            x, y = p[0], p[1]
        except:
            continue
        obs.add((clamp_int(x), clamp_int(y)))

    res = []
    for r in (observation.get("resources") or []):
        if r is None:
            continue
        try:
            x, y = r[0], r[1]
        except:
            continue
        res.append((clamp_int(x), clamp_int(y)))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    c += 1
        return c

    best = moves[0]
    bestv = -10**18
    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dnr = min(md((nx, ny), r) for r in res)
            dopr = md((nx, ny), (ox, oy))
            v = (-dnr * 10) + (dopr * 3) - obstacle_adj(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]
    else:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dct = md((nx, ny), (tx, ty))
            dopr = md((nx, ny), (ox, oy))
            v = (-dct * 6) + (dopr * 2) - obstacle_adj(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]

    return best