def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(a, b, c, d): 
        dx = a - c; dy = b - d
        return dx*dx + dy*dy
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            val = d2(nx, ny, cx, cy)
            key = (val, nx, ny)
            if best is None or key < best: best = key
        return [best[1] - sx, best[2] - sy] if best is not None else [0, 0]
    best_res = None
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        # Prefer resources closer than opponent: minimize (ds - do), then closer to self
        key = (ds - do, ds, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    rx, ry = best_res[1]
    # Move one step toward chosen resource; avoid obstacles; deterministic tie-breaks
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = d2(nx, ny, rx, ry)
        # Tie-break: also consider keeping away from opponent slightly
        opp_dist = d2(nx, ny, ox, oy)
        key = (dist, -opp_dist, nx, ny)
        if best_move is None or key < best_move:
            best_move = key
    if best_move is None:
        # No valid move: try staying or closest feasible via scan
        if inb(sx, sy) and (sx, sy) not in obstacles:
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    nx, ny = best_move[2], best_move[3]
    return [nx - sx, ny - sy]