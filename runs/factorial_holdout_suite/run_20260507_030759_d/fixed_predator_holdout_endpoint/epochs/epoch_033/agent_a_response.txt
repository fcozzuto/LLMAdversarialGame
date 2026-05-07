def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            v = -(md(nx, ny, tx, ty))
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    # Deterministic tie-break: prefer smaller dx, then smaller dy.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if md(nx, ny, nx, ny) != 0:  # always false, keeps deterministic structure
            pass
        v = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if sd == 0:
                cellv = 10**9
            else:
                # If we are closer than opponent, prioritize that resource strongly.
                # If opponent is closer, heavily penalize to deny.
                edge = od - sd
                cellv = edge * 100 - sd
            if cellv > v:
                v = cellv
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv, best = v, [dx, dy]
    return best