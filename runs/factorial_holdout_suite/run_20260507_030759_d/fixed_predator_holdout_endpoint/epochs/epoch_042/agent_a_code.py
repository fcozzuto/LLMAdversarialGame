def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def absmax(x, y):
        ax = x if x >= 0 else -x
        ay = y if y >= 0 else -y
        return ax if ax > ay else ay

    def obstacle_pen(x, y):
        if (x, y) in obs:
            return 1e9
        p = 0
        for a, b in obstacles:
            d = absmax(x - a, y - b)
            if d == 0:
                return 1e9
            if d == 1:
                p += 30
            elif d == 2:
                p += 6
        return p

    if resources:
        tgt = resources[0]
        bestd = 10**18
        for rx, ry in resources:
            d = absmax(sx - rx, sy - ry)
            if d < bestd:
                bestd = d
                tgt = (rx, ry)
        cx, cy = tgt
    else:
        cx, cy = (w // 2), (h // 2)

    bestv = -1e18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs:
            continue
        d_me = absmax(nx - cx, ny - cy)
        v = -d_me * 10
        if resources:
            for rx, ry in resources[:6]:
                if (nx, ny) == (rx, ry):
                    v += 5000
                else:
                    dr = absmax(nx - rx, ny - ry)
                    v += (20 if dr == 1 else 0) + (8 if dr == 2 else 0)
        d_opp = absmax(nx - ox, ny - oy)
        v += -d_opp * 1.2
        v -= obstacle_pen(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]