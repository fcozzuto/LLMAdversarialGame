def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        cx, cy = w // 2, h // 2
        tx = cx if cx != ox else (0 if ox > cx else w - 1)
        ty = cy if cy != oy else (0 if oy > cy else h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # Target scoring: prefer resources where we arrive sooner than opponent,
    # and (vs sweep-row nemesis) prefer shifting into different y bands.
    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_step_x = ox
        opp_step_y = oy
        # Opponent could move next; approximate by their ability to reduce Manhattan distance.
        # Use best-case single step improvement (max possible is 1 in L1 per axis move with diagonals).
        # This is a safe heuristic for determinism without full search.
        best_for_this_move = -10**18
        for rx, ry in res:
            d_us = man(nx, ny, rx, ry)
            # Opponent can reduce distance by at most 2 per move with diagonals, but L1 decreases by up to 2.
            d_opp = man(opp_step_x, opp_step_y, rx, ry)
            d_opp_next_best = max(0, d_opp - 2)
            arrival_adv = d_opp_next_best - d_us  # higher => we are closer
            y_band_pen = 0
            # Sweep-rows often attacks along a row/near-row; avoid that by preferring resources with y far from oy.
            y_band_pen = -0.35 * abs(ry - oy)
            # Also avoid immediate collisions with obstacles by nudging against resources that are "behind" blocked cells.
            # (Lightweight: just penalize resources adjacent to obstacles around our next position.)
            adj_obs = 0
            for ddx, ddy in moves:
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in obstacles:
                    adj_obs += 1
            adj_pen = -0.06 * adj_obs

            val = arrival_adv * 10.0 + y_band_pen + adj_pen - 0.02 * d_us
            if val > best_for_this_move:
                best_for_this_move = val

        # Small preference for progress: prefer moves that reduce distance to the best-scored resource next.
        # Determine direction by comparing to the resource that maximizes for this candidate.
        if best_for_this_move > best:
            best = best_for_this_move
            best_move = [dx, dy]

    return best_move