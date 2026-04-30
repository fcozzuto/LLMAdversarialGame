def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    res_list = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res_list.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not obs: return 0.0
        md = 99
        for px, py in obs:
            d = cheb(x, y, px, py)
            if d < md:
                md = d
                if md <= 0: break
        if md == 0: return 10.0
        if md == 1: return 2.3
        if md == 2: return 1.0
        return 0.0

    if not res_list:
        tx, ty = (0, 0) if (sx + sy) <= (w-1 + h-1 - (sx + sy)) else (w-1, h-1)
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = 0.9 * ((nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)) - 0.7 * ((nx - tx)*(nx - tx) + (ny - ty)*(ny - ty)) - obs_pen(nx, ny)
            if v > bestv: bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Candidate resource: prioritize ones we can reach sooner than opponent; otherwise, take best available and keep distance.
    best_move = (0, 0); best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue
        my_best = -10**18
        for rx, ry in res_list:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            reach_gap = do - dm  # positive means we are closer
            # Strongly prefer taking resources where we are not behind; otherwise prefer safer/distant options
            val = 4.0 * reach_gap - 1.2 * dm + 0.35 * ((nx - ox)*(nx - ox) + (ny - oy)*(ny - oy))
            my_best = val if val > my_best else my_best
        v = my_best - obs_pen(nx, ny)
        if v > best_val:
            best_val, best_move = v, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]