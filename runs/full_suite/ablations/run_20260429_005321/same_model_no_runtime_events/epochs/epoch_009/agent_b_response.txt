def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    live_res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not live_res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        # Proximity penalty to opponent (avoid getting too close unless winning races)
        opp_d = cheb(nx, ny, ox, oy)
        prox_pen = max(0, 3 - opp_d)

        # Race for a resource: maximize time advantage (opponent distance - our distance).
        # Break ties deterministically by favoring smaller our distance and then position.
        best_adv = None
        best_dist_key = None
        for rx, ry in live_res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # If opponent can grab this immediately and we are also close, prioritize blocking by keeping sd > od low.
            # Deterministic tie-break:
            dist_key = (-(adv), sd, od, rx, ry)
            if best_adv is None or dist_key < best_dist_key:
                best_adv = adv
                best_dist_key = dist_key

        # Capture/contest bonuses:
        cur_on_res = 1 if (nx, ny) in live_res else 0
        capture_bonus = 5 if cur_on_res else 0

        # Favor staying on/near resources while ensuring positive advantage.
        # Higher score is better: adv dominates, then our distance, then deterministic.
        sd_to_best = best_dist_key[1]
        od_to_best = best_dist_key[2]
        score_key = (
            -(best_adv + capture_bonus * 2),  # maximize advantage => minimize negative
            sd_to_best,                      # closer to target
            -max(0, best_adv),              # prefer positive advantage
            -cur_on_res,
            -opp_d,                          # slightly prefer staying farther
            dx, dy
        )

        if best_key is None or score_key < best_key:
            best_key = score_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]