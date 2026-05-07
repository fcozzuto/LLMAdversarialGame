def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0:
            ax = -ax
        ay -= by
        if ay < 0:
            ay = -ay
        return ax + ay

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_dxdy = [0, 0]
    best_gap = -10**18
    best_tdist = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best_gap = -10**18
        move_best_dist = 10**9
        move_has_pick = 0

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            gap = do - ds
            if ds == 0:
                move_has_pick = 1
                gap = 10**9
            if gap > move_best_gap or (gap == move_best_gap and ds < move_best_dist):
                move_best_gap = gap
                move_best_dist = ds

        if move_has_pick:
            score_gap = 10**8 + move_best_gap
        else:
            score_gap = move_best_gap

        if score_gap > best_gap or (score_gap == best_gap and move_best_dist < best_tdist):
            best_gap = score_gap
            best_tdist = move_best_dist
            best_dxdy = [dx, dy]

    return best_dxdy