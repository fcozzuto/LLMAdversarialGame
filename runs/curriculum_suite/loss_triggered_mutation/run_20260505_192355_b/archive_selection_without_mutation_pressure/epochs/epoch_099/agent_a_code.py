def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        best = None
        bx = None
        for dx, dy, nx, ny in cand:
            d = abs(nx - ox) + abs(ny - oy)
            t = d
            if best is None or t < best or (t == best and (dx, dy) < bx):
                best = t
                bx = (dx, dy)
        return [bx[0], bx[1]]

    bestv = None
    bestm = (0, 0)
    for dx, dy, nx, ny in cand:
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            if myd < my_best:
                my_best = myd
            if opd < opp_best:
                opp_best = opd
        value = (opp_best - my_best) - my_best * 0.01 - (nx + ny) * 0.0001
        if bestv is None or value > bestv or (value == bestv and (dx, dy) < bestm):
            bestv = value
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]