def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cur_best_margin = None
        cur_best_sd = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # assume opponent can reduce their distance by ~1 this turn
            od_eff = od - 1
            if od_eff < 0:
                od_eff = 0
            margin = od_eff - sd  # positive: we are ahead/at least not behind
            key2 = (margin, -sd, -rx, -ry)
            if cur_best_margin is None or key2 > (cur_best_margin, cur_best_sd, 0, 0):
                cur_best_margin = margin
                cur_best_sd = sd

        # secondary: prefer moves that also reduce opponent to our current top-choice resources blocking-wise
        # deterministic approximation: choose lower sum of distances to resource where we are most ahead
        # (by using cur_best_sd; larger margin already encodes opponent lead vs ours)
        score_key = (cur_best_margin, -cur_best_sd, -(abs(nx - ox) + abs(ny - oy)), -abs(nx - (w - 1)) - abs(ny - (h - 1)), dx, dy)
        if best_key is None or score_key > best_key:
            best_key = score_key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]