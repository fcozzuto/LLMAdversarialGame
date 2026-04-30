def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Precompute resource scores from current positions (used in 1-step lookahead evaluation)
    res_info = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are closer, high positive. Otherwise negative (we are being out-raced).
        base = (do - du) * 10 - du
        # Small bias toward resources that are "more contested" (both are close)
        contested = (du + do) * 0.01
        res_info.append((rx, ry, base - contested, du, do))

    if not res_info:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by picking the single best resource outcome after this move.
        # Prefer resources we are strictly closer to; if none, minimize how badly we lag.
        chosen_val = -10**18
        for rx, ry, base, _, _ in res_info:
            if (rx, ry) in obstacles:
                continue
            du2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)
            # Strict advantage term
            adv = (do2 - du2) * 10
            # If opponent can reach in <= our time, discourage strongly
            contest_pen = 0
            if du2 >= do2:
                contest_pen = (du2 - do2) * 50 + du2
            # Slight preference for nearer resources (even when tied)
            near_pref = -0.5 * du2
            # Use current base to break ties deterministically toward generally better resources
            tie = 0.001 * base
            val = adv - contest_pen + near_pref + tie

            if val > chosen_val:
                chosen_val = val

        # Additional strategic change: if we can immediately step closer to opponent, do it
        # when no resources give a clear advantage (reduces their distance to contested areas).
        if chosen_val < 0:
            opp_close = cheb(nx, ny, ox, oy)
            cur_close = cheb(sx, sy, ox, oy)
            chosen_val += (cur_close - opp_close) * 3

        if chosen_val > best_val:
            best_val = chosen_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]