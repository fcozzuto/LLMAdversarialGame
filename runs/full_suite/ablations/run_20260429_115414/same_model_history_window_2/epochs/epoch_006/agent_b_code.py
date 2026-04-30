def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) not in blocked:
            viable.append((rx, ry))

    if not viable:
        tx = 0 if sx > (w - 1) // 2 else (w - 1)
        ty = 0 if sy > (h - 1) // 2 else (h - 1)
        dx = 1 if tx > sx else (-1 if tx < sx else 0)
        dy = 1 if ty > sy else (-1 if ty < sy else 0)
        if (sx + dx, sy + dy) in blocked:
            for mx, my in moves:
                nx, ny = sx + mx, sy + my
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    return [mx, my]
        return [dx, dy]

    best = None
    best_key = None
    mycorner = 0 if (sx <= (w - 1) // 2) else (w - 1)
    mycorner2 = 0 if (sy <= (h - 1) // 2) else (h - 1)
    for rx, ry in viable:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        contest = od - myd
        corner_bias = -cheb(rx, ry, mycorner, mycorner2)
        key = (contest, -myd, corner_bias, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    bestm = None
    bestms = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        step_score = (od - myd, -myd, -cheb(nx, ny, mycorner, mycorner2), mx, my)
        if bestms is None or step_score > bestms:
            bestms = step_score
            bestm = (mx, my)

    if bestm is None:
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                return [mx, my]
        return [0, 0]
    return [bestm[0], bestm[1]]