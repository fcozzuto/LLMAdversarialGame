def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    if not res_list:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            cand = (-d, nx, ny, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[3], best[4]] if best is not None else [0, 0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Advantage: how much closer we are than opponent (bigger is better)
        max_adv = -10**9
        best_my_d = 10**9
        for rx, ry in res_list:
            dme = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - dme
            if adv > max_adv or (adv == max_adv and dme < best_my_d):
                max_adv = adv
                best_my_d = dme
        cand = (max_adv, -best_my_d, nx, ny, -dx, -dy)
        if best is None or cand > best:
            best = cand

    return [best[4], best[5]] if best is not None else [0, 0]