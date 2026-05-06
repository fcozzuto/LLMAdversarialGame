def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Choose a contested target: resource that makes (our_dist - opp_dist) as small as possible.
    best_t, best_gap = None, 10**9
    for rx, ry in resources:
        gap = man(sx, sy, rx, ry) - man(ox, oy, rx, ry)
        # Slightly favor resources near opponent's y (center-ish sweep behavior)
        gap += 0.25 * (abs(ry - oy))
        if gap < best_gap:
            best_gap, best_t = gap, (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)

        # If we can get closer than opponent (or tie), increase priority strongly.
        contest = (opp_d - my_d)

        # Also consider not letting opponent advance to other resources near their row.
        opp_row_target = None
        opp_row_pen = 10**9
        for rx, ry in resources:
            rpen = abs(ry - oy)
            if rpen < opp_row_pen:
                opp_row_pen, opp_row_target = rpen, (rx, ry)
        orx, ory = opp_row_target
        my_other = man(nx, ny, orx, ory)
        opp_other = man(ox, oy, orx, ory)
        deny = (my_other - opp_other)

        # Keep movement purposeful: slight penalty for moving away from the chosen target.
        step_pen = my_d - man(sx, sy, tx, ty)

        score = 5.0 * contest - 2.0 * deny - 0.3 * step_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]