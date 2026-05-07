def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = [0, 0]
    best_score = -10**18

    # Precompute opponent distances to each resource
    res_info = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        res_info.append((rx, ry, man(ox, oy, rx, ry)))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best = -10**18
        for rx, ry, do in res_info:
            ds = man(nx, ny, rx, ry)
            lead = do - ds  # positive => we are closer than opponent

            # Urgency if opponent can grab immediately; push to targets that deny
            # (denier tends to race; being within 1 of a resource matters)
            opp_immediate = 1 if do <= 1 else 0

            # If we reach now, prioritize hard
            if ds == 0:
                score = 10**12
            else:
                # Prefer higher lead, then smaller self distance, and slightly prefer farther opponent
                score = lead * 10**6 - ds * 50 - opp_immediate * 500

                # Extra preference for resources that are also "common sense safe": we shouldn't be behind badly
                if lead < -2:
                    score -= 2000

            if score > move_best:
                move_best = score

        # Global tie-breaker: prefer moves that keep us nearer to the closest resource
        if move_best > best_score:
            best_score = move_best
            best = [dx, dy]
        elif move_best == best_score:
            cur_ds_best = 10**9
            best_ds = 10**9
            for rx, ry, _do in res_info:
                ds1 = man(sx + best[0], sy + best[1], rx, ry)
                ds2 = man(nx, ny, rx, ry)
                if ds1 < best_ds:
                    best_ds = ds1
                if ds2 < cur_ds_best:
                    cur_ds_best = ds2
            if cur_ds_best < best_ds:
                best = [dx, dy]

    return best