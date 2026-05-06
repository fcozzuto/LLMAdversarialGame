def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    opp_center_bias = man(ox, oy, (w - 1) // 2, (h - 1) // 2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Evaluate by "win" margin against opponent over the best available resource.
        my_best = 10**9
        margin_best = -10**9
        nearest_to_me = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if myd < nearest_to_me:
                nearest_to_me = myd
            margin = opd - myd
            if margin > margin_best:
                margin_best = margin

        # Prefer moves that secure a positive margin; else still reduce nearest distance.
        # Deterministic tie-break: prefer smaller my_best, then larger margin, then closer to board center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_dist = man(nx, ny, cx, cy)
        key = (
            -(margin_best if margin_best > 0 else 0),   # maximize positive margin
            nearest_to_me,                               # then get closer to something
            -margin_best,                                 # then maximize overall margin
            center_dist,                                  # then center-ish (deterministic tie break)
            man(nx, ny, ox, oy),                          # then away/toward opponent deterministically
            opp_center_bias
        )
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best:
        return [int(best[1]), int(best[2])]
    return [0, 0]