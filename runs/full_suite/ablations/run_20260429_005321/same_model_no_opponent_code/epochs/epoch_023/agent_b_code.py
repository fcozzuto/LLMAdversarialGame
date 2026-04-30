def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set()
    obstacles = observation.get("obstacles") or []
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obs:
                res.append((rx, ry))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = (man(nx, ny, cx, cy), man(nx, ny, ox, oy), dx, dy)
            if best is None or v < best:
                best = v
        return [best[2], best[3]]

    best_move = None
    for dx, dy, nx, ny in moves:
        best_adv = -10**9
        best_tie = None
        for rx, ry in res:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = (d_op - d_me)
            if d_me == 0:
                adv = 10**6
            # Prefer winning a resource sooner; then smaller my distance; then deterministic tie.
            if adv > best_adv:
                best_adv = adv
                best_tie = (d_me, d_op, rx, ry)
            elif adv == best_adv and best_tie is not None:
                cand = (d_me, d_op, rx, ry)
                if cand < best_tie:
                    best_tie = cand
        # Secondary: after choosing a resource, prefer moves that keep away from opponent.
        op_dist = man(nx, ny, ox, oy)
        cand_move = (-(best_adv), best_tie[0], -op_dist, dx, dy)
        if best_move is None or cand_move < best_move:
            best_move = cand_move

    return [best_move[3], best_move[4]]