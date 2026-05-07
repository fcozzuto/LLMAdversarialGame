def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not valid(sx, sy):
        sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
        sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a target resource where we are at least as fast as opponent, otherwise maximize relative advantage.
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key: prefer those we can win (sd<=od), then larger margin (od-sd), then closer distance.
        winflag = 1 if sd <= od else 0
        key = (winflag, od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = [rx, ry]

    rx, ry = best_target[0], best_target[1]

    # One-step evaluation: move to the best neighboring cell for the chosen target, with a small penalty if moving away.
    best = [0, 0]
    bestv = -10**18
    curd = cheb(sx, sy, rx, ry)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        # Prefer reducing distance; break ties by improving our lead over opponent on that same target.
        self_gain = curd - nd
        od_now = cheb(ox, oy, rx, ry)
        opp_gain = od_now - nd
        v = (self_gain * 100) + (opp_gain) - (1 if (nx == rx and ny == ry) else 0)
        # Small deterministic tie-break by position
        v += (-nx - ny) * 1e-3
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best