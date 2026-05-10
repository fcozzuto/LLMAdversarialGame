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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_key = None  # (adv, -sd, row_bias, col_bias, -od, sd, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose target resource that maximizes our lead over opponent
        chosen = None
        chosen_sd = None
        chosen_od = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Prefer breaking ties toward closer target; opponent farther helps.
            key = (adv, -sd, od, sd)
            if chosen is None or key > chosen:
                chosen = key
                chosen_sd, chosen_od = sd, od

        if chosen is None:
            continue

        # Small deterministic bias against sweep_rows: prefer progressing in the dimension opponent is likely scanning.
        row_bias = -abs(ny - oy)
        col_bias = -abs(nx - ox)

        adv, neg_sd, od_t, sd_t = chosen
        sd = chosen_sd
        od = chosen_od
        key = (adv, -sd, row_bias, col_bias, -od, sd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move