def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in srole) or ("evasion" in srole) or ("evader" in orole and "pursuer" in srole)
    opp_is_evader = not self_is_evader

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    t = int(observation.get("turn_index", 0) or 0)
    if t & 1:
        dirs = dirs[5:] + dirs[:5]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def neighbors(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                yield dx, dy, nx, ny

    def predict_opp(posx, posy, ourx, oury, opp_evader):
        # Greedy 1-step prediction: if opponent is evader -> maximize distance; else minimize.
        best = None
        for dx, dy, nx, ny in neighbors(posx, posy):
            ddx, ddy = nx - ourx, ny - oury
            d2 = ddx * ddx + ddy * ddy
            val = d2 if opp_evader else -d2
            if best is None or val > best[0]:
                best = (val, dx, dy, nx, ny)
        return (best[3], best[4]) if best else (posx, posy)

    px, py = predict_opp(ox, oy, sx, sy, opp_is_evader)

    # Opponent-predicted chase/flee
    best_move = (None, None, -10**18)
    for dx, dy, nx, ny in neighbors(sx, sy):
        ddx, ddy = nx - px, ny - py
        d2 = ddx * ddx + ddy * ddy
        # Tiny obstacle/boundary preference to avoid getting stuck in corners/near blocks
        boundary_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
        obst_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obst:
                    obst_adj += 1
        if self_is_evader:
            val = d2 - 2 * obst_adj - 0.5 * boundary_pen
        else:
            val = -d2 - 2 * obst_adj - 0.5 * boundary_pen
        if val > best_move[2]:
            best_move = (dx, dy, val)

    return [int(best_move[0] or 0), int(best_move[1] or 0)]