def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target selection: contest first, but add pressure on resources aligned with opponent (good vs row sweep).
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        contest_gap = od - sd  # higher means we are closer
        align_bonus = 0
        if ry == oy:
            align_bonus += 3  # share row with opponent
        if rx == ox:
            align_bonus += 1  # share column occasionally helps
        # Key: maximize contest_gap + align_bonus, then minimize our distance, then stable tie-break.
        key = (-(contest_gap + align_bonus), sd, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_eval = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        myd = man(nx, ny, rx, ry)

        # One-step contest improvement: prefer moves that increase (opp_dist - my_dist) or approach target.
        oppd = man(ox, oy, rx, ry)
        eval1 = myd - oppd  # smaller is better (we being closer => more negative)

        # Secondary: reduce distance to "row-aligned" resources if immediate contest is weak.
        row_target = None
        row_best = None
        for px, py in resources:
            if py == oy:
                d = man(nx, ny, px, py)
                if row_best is None or d < row_best:
                    row_best = d
                    row_target = (px, py)
        eval2 = row_best if row_target is not None else 99

        # Final deterministic tie-break.
        key = (eval1, eval2, myd, (nx, ny))
        if best_eval is None or key < best_eval:
            best_eval = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]