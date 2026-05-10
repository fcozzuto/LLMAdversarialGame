def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    dx_sign = 0 if sx == ox else (1 if sx > ox else -1)
    dy_sign = 0 if sy == oy else (1 if sy > oy else -1)

    def quad_bias(rx, ry):
        # Favor resources on our side of the board relative to opponent corner/sweep tendency
        bx = (sx - rx) * dx_sign
        by = (sy - ry) * dy_sign
        return bx + by

    best_move = [0, 0]
    best_key = None  # maximize key

    for mvx, mvy in dirs:
        nx, ny = sx + mvx, sy + mvy
        if not ok(nx, ny):
            continue
        # Evaluate best target resource if we move here
        local_best = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd == 0:
                adv = od + 5
            else:
                adv = od - sd  # prefer resources where we are closer than opponent
            key = (adv * 10, quad_bias(rx, ry), -sd)
            if local_best is None or key > local_best:
                local_best = key
        if local_best is None:
            continue
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = [mvx, mvy]

    return [int(best_move[0]), int(best_move[1])]