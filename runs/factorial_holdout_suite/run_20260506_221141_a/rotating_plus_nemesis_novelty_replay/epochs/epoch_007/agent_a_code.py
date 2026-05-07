def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return None

    obs = set()
    for o in obstacles:
        q = norm_pos(o)
        if q:
            obs.add(q)

    res = []
    for r in resources:
        q = norm_pos(r)
        if q:
            res.append(q)
    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best = 10**9
        op_best = 10**9
        best_gap = -10**9
        for rx, ry in res:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            if myd < my_best:
                my_best = myd
            if opd < op_best:
                op_best = opd
            gap = opd - myd
            if gap > best_gap:
                best_gap = gap

        sc = 0
        if my_best == 0:
            sc = 10**12
        else:
            sc = best_gap * 1000 - my_best
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]