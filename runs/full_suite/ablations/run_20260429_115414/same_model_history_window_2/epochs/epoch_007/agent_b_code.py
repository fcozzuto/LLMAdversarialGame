def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in blocked

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in blocked:
            viable.append((rx, ry))

    # Choose best target by contesting preference: us earlier > us closer > deterministic tie-break.
    if viable:
        best = None; best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            belt = abs((rx + ry) - (sx + sy))
            key = (-(od - myd), myd, belt, rx, ry)  # maximize (od-myd), minimize myd
            if best_key is None or key < best_key:
                best_key = key; best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: go to our corner.
        tx = 0 if sx <= (w - 1) // 2 else (w - 1)
        ty = 0 if sy <= (h - 1) // 2 else (h - 1)

    # Deterministically move toward (tx,ty), with local obstacle avoidance.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    primary = (sx + dx, sy + dy)

    def score_step(nx, ny):
        # Prefer getting closer to target and not letting opponent get much closer.
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        belt = abs((tx + ty) - (nx + ny))
        # Lower is better:
        return (myd - od, myd, belt, nx, ny)

    if legal(primary[0], primary[1]):
        return [dx, dy]

    # If blocked, pick best among legal moves.
    best_mv = None; best_st = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not legal(nx, ny): 
            continue
        st = score_step(nx, ny)
        if best_st is None or st < best_st:
            best_st = st; best_mv = (mx, my)

    if best_mv is None:
        return [0, 0]
    return [best_mv[0], best_mv[1]]