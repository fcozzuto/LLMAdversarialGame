def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    # Immediate pick if available
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    if not res_list:
        # Head toward opponent corner-ish deterministically
        tx = 0 if ox > sx else (w - 1)
        ty = 0 if oy > sy else (h - 1)
        best = None; bestd = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d; best = [dx, dy]
        return best if best is not None else [0, 0]

    # Choose move that maximizes advantage vs opponent on best resource
    best_move = [0, 0]; best_adv = -10**9; best_selfd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        adv = -10**9
        selfd_best = 10**9
        for rx, ry in res_list:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            a = od - sd
            if a > adv or (a == adv and sd < selfd_best):
                adv = a
                selfd_best = sd
        if adv > best_adv or (adv == best_adv and selfd_best < best_selfd):
            best_adv = adv; best_selfd = selfd_best; best_move = [dx, dy]

    return best_move