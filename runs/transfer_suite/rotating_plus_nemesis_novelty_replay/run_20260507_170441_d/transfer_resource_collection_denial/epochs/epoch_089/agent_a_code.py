def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not resources:
        tx, ty = w - 1, h - 1
        if cheb(sx, sy, tx, ty) > cheb(sx, sy, 0, 0):
            tx, ty = 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        adv = op_d - my_d  # positive: we are closer
        # Prefer resources we can reach sooner than opponent; otherwise still progress.
        v = adv * 2000 - my_d * 6 - (rx * 0.0 + ry * 0.0)
        # Small deterministic tie-break to reduce dithering.
        v -= (rx * 31 + ry * 17) * 0.0001
        if v > bestv:
            bestv = v
            best = (rx, ry)

    rx, ry = best

    # Choose best immediate move among legal neighbors to reach the chosen target.
    bestm = (0, 0)
    bestmv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d2 = cheb(nx, ny, rx, ry)
        op_d2 = cheb(ox, oy, rx, ry)
        adv2 = op_d2 - my_d2
        # Encourage lowering distance; also avoid moves that increase distance too much.
        mv = adv2 * 2000 - my_d2 * 10 - (0.001 * (nx * 29 + ny * 23))
        if mv > bestmv:
            bestmv = mv
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]