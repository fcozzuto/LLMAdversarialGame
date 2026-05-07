def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set(tuple(r) for r in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        if inb(sx + tx, sy): return [tx, 0]  # deterministic preference
        if inb(sx, sy + ty): return [0, ty]
        return [0, 0]

    best_move = None
    best_adv = -10**9
    best_my = 10**9
    best_t = 10**9

    # deterministic tie-breaker order already in dirs
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_best = 10**9
        adv_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > adv_best:
                adv_best = adv; my_best = myd
            elif adv == adv_best and myd < my_best:
                my_best = myd
        # tertiary bias: move closer to center to reduce pathing loops
        center = (w - 1) / 2.0
        t = abs(nx - center) + abs(ny - (h - 1) / 2.0)
        if (adv_best > best_adv) or (adv_best == best_adv and my_best < best_my) or (adv_best == best_adv and my_best == best_my and t < best_t):
            best_adv = adv_best; best_my = my_best; best_t = t; best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]