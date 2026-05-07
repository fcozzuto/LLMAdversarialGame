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
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    opp_adj = set()
    for dx, dy in dirs:
        px, py = ox + dx, oy + dy
        if inb(px, py) and (px, py) in res_set:
            opp_adj.add((px, py))

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if nx == sx and ny == sy and not resources:
            return [0, 0]

        my_best_key = None
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - dme  # larger is better
            # If opponent can take it immediately next, penalize it.
            imm = 1 if (rx, ry) in opp_adj else 0
            key = (margin, -imm, -dme, -cheb(nx, ny, rx, ry), -abs(rx - ox) - abs(ry - oy), rx, ry)
            if my_best_key is None or key > my_best_key:
                my_best_key = key

        # If no resources, just stay.
        if my_best_key is None:
            cur_key = (0, -0, -0, 0)
        else:
            # Use my_best_key directly but also mildly prefer actions that move away from being stuck.
            cur_key = my_best_key + (-(abs(nx - sx) + abs(ny - sy)),)

        if best is None or cur_key > best[0]:
            best = (cur_key, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]