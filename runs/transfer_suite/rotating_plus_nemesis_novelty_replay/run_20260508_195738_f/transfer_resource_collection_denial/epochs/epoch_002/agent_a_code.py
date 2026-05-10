def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = observation.get("resources", []) or []

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best = None
        bestv = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            v = (oppd - myd) * 1000 - myd
            if bestv is None or v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        # move toward the corner farthest from opponent
        tx, ty = None, None
        bestv = None
        for cx, cy in corners:
            v = -cheb(ox, oy, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (cx, cy) < (tx, ty)):
                bestv = v
                tx, ty = cx, cy

    bestmove = (0, 0)
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # prefer decreasing myd; also prefer moves that keep distance from opponent slightly
        odist = cheb(nx, ny, ox, oy)
        score = (oppd - myd) * 1000 - myd - odist
        if bestscore is None or score > bestscore:
            bestscore = score
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]