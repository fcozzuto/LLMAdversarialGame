def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = observation.get("turn_index", 0)

    # Opponent's current nearest resource (deterministic tie by coords)
    opp_nearest = None
    opp_best = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        key = (d, rx, ry)
        if opp_best is None or key < opp_best:
            opp_best = key
            opp_nearest = (rx, ry)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        my_best = None
        my_best_key = None
        deny_score = 0
        take_score = 0

        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # Prefer taking resources we can beat (or tie) from next step.
            if d_my <= d_op:
                # Closer beats further; also slightly prefer cells closer to opponent's nearest.
                take_score += (10 - d_my)
            # If we are strictly closer than opponent, "deny" their likely path.
            if d_my < d_op:
                deny_score += (6 - d_op + d_my)

            key = (d_my, rx, ry)
            if my_best_key is None or key < my_best_key:
                my_best_key = key
                my_best = (rx, ry)

        # Tactical: also try to reduce distance to the resource opponent is aiming for.
        rx0, ry0 = opp_nearest
        opp_focus_dist_before = cheb(ox, oy, rx0, ry0)
        opp_focus_dist_after = cheb(nx, ny, rx0, ry0)

        # Make "center-seeking" when tied/no resources near.
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - center_x) + abs(ny - center_y)

        val = 0
        val += 3 * (take_score + deny_score)
        val += (20 - my_best_key[0]) if my_best_key is not None else 0
        val += (12 - opp_focus_dist_after)  # approach contested target
        val += -0.01 * center_dist

        # Deterministic tie-break by favoring moves that progress in the "sweep" direction alternation.
        sweep_bias = (dx, dy)
        if (ti & 1) == 1:
            sweep_bias = (dy, dx)
        val += 0.001 * (sweep_bias[0] * 3 + sweep_bias[1])

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]