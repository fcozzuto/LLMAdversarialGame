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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    # Precompute resource list (deterministic)
    valid_res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if ok(rx, ry) or (rx, ry) in obstacles:
            # If resource sits on blocked tile, still treat it as target (engine may ignore obstacles for resources)
            valid_res.append((rx, ry))
    if not valid_res:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose resource that maximizes my advantage, but also favor moves that deny opponent's near-term access
        my_best_adv = -10**9
        deny_term = -10**9
        tie_my = None

        for rx, ry in valid_res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive = I get closer than opponent
            if (tie_my is None) or adv > my_best_adv or (adv == my_best_adv and sd < tie_my[0]):
                my_best_adv = adv
                tie_my = (sd, rx, ry)

        # Deny: how much my move increases opponent's distance to the best "I-advantage" target
        if tie_my is not None:
            sd, rx, ry = tie_my
            opp_sd = md(ox, oy, rx, ry)
            deny_term = opp_sd - sd  # same target, but keep explicit deterministic term

        # Risk control: avoid getting stuck behind obstacles by lightly penalizing distance to nearest resource
        nearest_sd = 10**9
        for rx, ry in valid_res:
            d = md(nx, ny, rx, ry)
            if d < nearest_sd:
                nearest_sd = d

        val = (my_best_adv, deny_term, -nearest_sd)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move