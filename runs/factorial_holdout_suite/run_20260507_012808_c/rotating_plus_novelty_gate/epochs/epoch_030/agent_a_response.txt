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

    if not valid(sx, sy):
        sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
        sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources or w <= 0 or h <= 0:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestv, bestm = -10**18, [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    bestv, bestm = -10**18, [0, 0]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        my_min = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            advantage = opd - myd  # positive means we are closer
            # encourage fast wins and deny opponent
            v = (advantage * 10) - (myd) - (opd if opd < myd else 0) * 0.25
            if v > my_min:
                my_min = v
        # slight preference for staying mobile toward any resource
        if my_min > bestv or (my_min == bestv and (dxm, dym) != (0, 0) and bestm == [0, 0]):
            bestv, bestm = my_min, [dxm, dym]
    return bestm