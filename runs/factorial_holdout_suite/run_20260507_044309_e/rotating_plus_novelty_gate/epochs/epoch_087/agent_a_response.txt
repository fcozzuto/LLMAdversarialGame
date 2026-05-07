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
        best = None; bestk = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            k = cheb(nx, ny, ox, oy)
            if best is None or k < bestk:
                best, bestk = [dx, dy], k
        return best if best is not None else [0, 0]

    def best_margin(x, y):
        best = -10**9
        for rx, ry in res_list:
            m = cheb(ox, oy, rx, ry) - cheb(x, y, rx, ry)
            if m > best:
                best = m
        return best

    best = [0, 0]; best_score = -10**18; best_tieb = 10**18
    for dx, dy in dirs:
        n1x, n1y = sx + dx, sy + dy
        if not inb(n1x, n1y):
            continue
        # 2-step deterministic lookahead: choose worst move opponent doesn't influence; we just look ahead our best response
        s1 = best_margin(n1x, n1y)
        s2 = -10**18
        for ddx, ddy in dirs:
            n2x, n2y = n1x + ddx, n1y + ddy
            if not inb(n2x, n2y):
                continue
            m = best_margin(n2x, n2y)
            if m > s2:
                s2 = m
        # Prefer immediate capture potential (already handled), then maximal advantage; tie-break by minimizing distance to best resource
        score = 2 * s1 + s2
        tieb = cheb(n1x, n1y, ox, oy)
        if score > best_score or (score == best_score and tieb < best_tieb):
            best_score, best_tieb, best = score, tieb, [dx, dy]
    return best