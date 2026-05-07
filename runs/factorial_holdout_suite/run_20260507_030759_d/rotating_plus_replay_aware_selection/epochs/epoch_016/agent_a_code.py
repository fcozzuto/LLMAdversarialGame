def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = obstacles if isinstance(obstacles, set) else set(tuple(p) for p in obstacles)

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    if not resources:
        return [0, 0]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        v = (do - ds) * 120 - ds * 5
        if v > bestv or (v == bestv and (rx, ry) < best):
            bestv = v
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    bestm = None
    bestmv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = man(nx, ny, tx, ty)
        ndo = man(ox, oy, tx, ty)
        mv = (ndo - nds) * 120 - nds * 7
        if bestm is None or mv > bestmv or (mv == bestmv and (dx, dy) < bestm):
            bestmv = mv
            bestm = (dx, dy)

    if bestm is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [bestm[0], bestm[1]]