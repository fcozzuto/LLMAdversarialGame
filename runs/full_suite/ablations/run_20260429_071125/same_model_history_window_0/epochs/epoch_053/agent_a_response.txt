def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    blocked = obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    resources = [r for r in resources if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in blocked]
    if not resources:
        tx, ty = 0, 0
    else:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            val = (opd - myd) * 10 - myd  # prefer resources I can reach sooner than opponent
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    # If already on target, step to the best next resource deterministically
    if (sx, sy) == (tx, ty) and resources:
        # pick resource maximizing my advantage among remaining not equal to current
        best = None
        best_val = -10**9
        for rx, ry in resources:
            if (rx, ry) == (sx, sy):
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            val = (opd - myd) * 10 - myd
            if val > best_val:
                best_val = val
                best = (rx, ry)
        if best is not None:
            tx, ty = best

    # Choose move: avoid obstacles; primarily reduce distance to (tx,ty); secondarily avoid moving into opponent proximity
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            return -10**9
        if (nx, ny) in blocked:
            return -10**8
        d = cheb(nx, ny, tx, ty)
        # small penalty if getting closer to opponent (deny less when contesting)
        opp_close = 0
        if observation.get("opponent_position") is not None:
            opp_close = cheb(nx, ny, ox, oy)
        return -d * 100 - (10 - opp_close)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        sc = score_move(dx, dy)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]