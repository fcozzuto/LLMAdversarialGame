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
            if (x + dx, y + dy) in obs: c += 1
        return c

    cx, cy = w // 2, h // 2

    if not res:
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            v = 1.5 * cheb(nx, ny, ox, oy) - 0.6 * cheb(nx, ny, cx, cy) - 2.0 * obs_near(nx, ny)
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_r = res[0]; best_adv = -10**18
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # bigger means we're closer relative to opponent
        if adv > best_adv:
            best_adv = adv; best_r = (rx, ry)

    tx, ty = best_r
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        chase = -1.9 * sd + 1.1 * od
        avoid = -2.1 * obs_near(nx, ny)
        center = -0.08 * cheb(nx, ny, cx, cy)
        opp_threat = -0.15 * cheb(nx, ny, ox, oy)  # keep some distance unless target changes
        v = chase + avoid + center + opp_threat
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]