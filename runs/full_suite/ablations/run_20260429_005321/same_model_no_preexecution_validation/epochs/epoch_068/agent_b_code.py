def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def obs_near(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: c += 1
        return c

    if not res:
        best_move = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            dcent = cheb(nx, ny, w//2, h//2)
            dopp = cheb(nx, ny, ox, oy)
            v = (2.0 * dopp) - (1.0 * dcent) - (2.0 * obs_near(nx, ny))
            if v > bestv: bestv = v; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_move = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): continue
        myd_min = 10**9; opd_min = 10**9
        myd2 = 10**9; opd2 = 10**9
        for rx, ry in res:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 < myd_min: myd2 = myd_min; myd_min = d1
            elif d1 < myd2: myd2 = d1
            if d2 < opd_min: opd2 = opd_min; opd_min = d2
            elif d2 < opd2: opd2 = d2

        dopp = cheb(nx, ny, ox, oy)
        obs_pen = obs_near(nx, ny)

        # Prefer moves that are closer to some resource than opponent, and reduce opponent's access.
        # Also slightly prefer increasing separation to avoid being blocked.
        winish = 0
        for rx, ry in res:
            if cheb(nx, ny, rx, ry) <= cheb(ox, oy, rx, ry): winish += 1

        target_pressure = (opd_min - myd_min)  # positive if we are closer to the closest resource than opp
        v = (3.0 * target_pressure) + (0.8 * winish) + (0.15 * (dopp)) - (1.0 * obs_pen)
        # If we are behind, attempt to deny: maximize distance to opponent for their best resource
        if myd_min > opd_min:
            v -= 0.35 * myd_min
            v += 0.25 * (opd_min - opd2)  # if opponent has one clear best, we should pressure

        if v > bestv:
            bestv = v; best_move = (dx, dy)

    return [best_move[0], best_move[1]]