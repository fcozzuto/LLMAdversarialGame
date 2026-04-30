def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obs:
                c += 1
        return c

    if not res:
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -0.4 * cheb(nx, ny, ox, oy) - 1.2 * near_obs(nx, ny)
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    # Pick target where we are ahead (opp_dist - our_dist high). Break ties by closeness.
    best_t = res[0]; best_s = -10**18
    for rx, ry in res:
        ourd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        safety = cheb(rx, ry, cx, cy) * 0.01
        s = (oppd - ourd) - 0.25 * ourd - safety
        if s > best_s:
            best_s = s; best_t = (rx, ry)

    rx, ry = best_t
    cur_adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)

    # One-step policy: reduce our distance to target; if multiple, prefer increasing distance to opponent and avoid obstacles.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ourd2 = cheb(nx, ny, rx, ry)
        oppd2 = cheb(ox, oy, nx, ny)
        adv2 = (cheb(ox, oy, rx, ry) - ourd2)
        # If we're not ahead, prioritize staying further from opponent while still steering to the target.
        v = 2.2 * adv2 - 0.9 * ourd2 + 0.35 * oppd2 - 1.0 * near_obs(nx, ny)
        if cur_adv <= 0:
            v += 1.2 * cheb(nx, ny, ox, oy)
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]