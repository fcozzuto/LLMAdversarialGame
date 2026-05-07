def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_k = (-10**9, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            k = (-d, d)
            if k > best_k:
                best_k = k
                best = [dx, dy]
        return best

    opp_mu = 0
    self_mu = 0
    # quick estimate: choose target set by relative closeness
    res_tuples = [tuple(r) for r in resources]
    for rx, ry in res_tuples:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if od <= sd:
            opp_mu += 1
        else:
            self_mu += 1
    prefer_race = opp_mu > self_mu  # if opponent tends to be ahead, prioritize bigger advantage picks

    best_move = [0, 0]
    best_key = (-10**18, -10**18, 10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        local_best_adv = -10**18
        local_best_sd = 10**18
        local_best_od = 10**18

        for rx, ry in res_tuples:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d
            # slight preference to resources we are closer to; stronger if opponent likely ahead
            if prefer_race:
                # maximize chance to beat opponent: prefer higher adv, then shorter self distance
                key_cmp = (adv, -self_d, self_d + (0 if self_d <= self_mu else 1), -opp_d)
            else:
                key_cmp = (adv, -opp_d, -self_d, self_d)

            # Convert to scalar for deterministic comparisons without storing tuples too much
            if key_cmp[0] > local_best_adv or (key_cmp[0] == local_best_adv and self_d < local_best_sd):
                local_best_adv = adv
                local_best_sd = self_d
                local_best_od = opp_d

        # tie-break: prefer directly moving toward some resource; then avoid staying if another legal move ties well
        toward = 0
        if resources:
            toward = min(cheb(nx, ny, r[0], r[1]) for r in res_tuples)  # small list, ok
        key = (local_best_adv, -(local_best_od), -local_best_sd, -toward)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move