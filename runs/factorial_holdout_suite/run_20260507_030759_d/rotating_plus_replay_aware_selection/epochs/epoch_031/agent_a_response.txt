def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_tuple = None  # (lead_score, -my_dist, idx)
    for idx, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_for_move = -10**18
        best_my_dist = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Primary: being closer than opponent (opp - my). Secondary: prefer pickup sooner.
            lead = do - ds
            val = lead * 1000 - ds
            if val > best_for_move or (val == best_for_move and ds < best_my_dist):
                best_for_move = val
                best_my_dist = ds
        t = (best_for_move, -best_my_dist, idx)
        if best_tuple is None or t > best_tuple:
            best_tuple = t
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best