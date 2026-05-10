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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best = None  # (better, we_can_win_flag, adv_margin, tie_break, -opp_d, sd, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_resource = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv_margin = od - sd
            # Prefer resources we can reach strictly before opponent; otherwise race on smallest gap.
            we_can_win = 1 if adv_margin > 0 else 0
            if best_resource is None:
                best_resource = (we_can_win, adv_margin, sd, od, rx, ry)
            else:
                b_win, b_adv, b_sd, b_od, _, _ = best_resource
                # primary: win-ness, then adv margin, then our distance, then opponent distance
                if (we_can_win, adv_margin, -sd, -od) > (b_win, b_adv, -b_sd, -b_od):
                    best_resource = (we_can_win, adv_margin, sd, od, rx, ry)

        we_can_win, adv_margin, sd, od, rx, ry = best_resource
        # tie-break: if equal advantage, go to closer resource; small preference for centralish
        centerish = -abs((w - 1) / 2 - nx) - abs((h - 1) / 2 - ny)
        score_key = (we_can_win, adv_margin, centerish, -sd, -od)
        if best is None or score_key > best[0]:
            best = (score_key, we_can_win, adv_margin, sd, od, dx, dy)

    return [int(best[5]), int(best[6])]