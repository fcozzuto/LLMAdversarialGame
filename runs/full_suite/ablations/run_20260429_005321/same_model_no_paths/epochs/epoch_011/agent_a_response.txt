def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    best_move = (0, 0)
    best_score = None

    if not resources:
        tx, ty = w - 1, h - 1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer moving toward own far-corner target while reducing obstacle pressure.
            score = man(nx, ny, tx, ty) + 0.25 * obs_pen(nx, ny)
            if best_score is None or score < best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]

    # Deterministic tie-break order by move list iteration.
    # Score: prioritize reducing our distance to the chosen target and preventing opponent proximity.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        np = obs_pen(nx, ny)

        # Choose target that we would reach best from nx,ny.
        best_target = None
        best_d = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if best_d is None or d < best_d:
                best_d, best_target = d, (rx, ry)
        rx, ry = best_target

        our_dist_next = best_d
        opp_dist_cur = man(ox, oy, rx, ry)
        opp_best_next = None
        # Consider opponent's best next step for that same target (local one-ply).
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d2 = man(tx, ty, rx, ry)
            if opp_best_next is None or d2 < opp_best_next:
                opp_best_next = d2
        if opp_best_next is None:
            opp_best_next = opp_dist_cur

        # Lower is better for us:
        # - Reduce our distance to the target.
        # - Increase opponent's best reachable distance (negative pressure).
        # - Slightly prefer keeping distance parity advantage.
        score = (our_dist_next
                 - 0.9 * (opp_dist_cur - opp_best_next)
                 + 0.35 * np)

        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]