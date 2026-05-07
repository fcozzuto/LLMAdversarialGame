def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res or (sx, sy) in obst:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evaluate resources by being closer than opponent (denial), then by proximity, then position.
    best = None
    best_key = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources we can beat; strong boost when ahead; deterministic tie-break.
        ahead = od - sd
        score_key = (ahead >= 1, ahead, -sd, -(tx + 17 * ty))
        if best_key is None or score_key > best_key:
            best_key = score_key
            best = (tx, ty)
    tx, ty = best

    # Choose move that reduces distance to target and avoids obstacles.
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if (mx == 0 and my == 0) or (mx != 0 or my != 0):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    d = cheb(nx, ny, tx, ty)
                    # slight penalty for moving toward opponent to counter denier
                    opp_d = cheb(nx, ny, ox, oy)
                    candidates.append((d, -opp_d, mx, my))
    # Deterministic: min distance, then max opponent distance, then lexicographic mx,my.
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]