def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    res = [tuple(p) for p in resources]
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target resource with emphasis on denying the opponent and setting up an intercept.
    best_move = (None, -10**18)  # (dx,dy), score
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue

        # Score this move by best achievable target under an "intercept halfway" plan.
        move_score = -10**18
        for rx, ry in res:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Mid-intercept point between opponent and resource (clamped to grid).
            mx = (ox + rx) // 2
            my = (oy + ry) // 2
            if mx < 0: mx = 0
            elif mx >= w: mx = w - 1
            if my < 0: my = 0
            elif my >= h: my = h - 1
            # Penalize if the opponent is much closer, and reward ability to reach intercept sooner.
            intercept_d = man(nx, ny, mx, my)
            opp_to_intercept = man(ox, oy, mx, my)
            # Slight obstacle penalty: prefer staying away from obstacles around candidate square.
            obs_near = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if (nx + ax, ny + ay) in obstacles:
                        obs_near += 1
            s = (opp_d - our_d) * 10 + (opp_to_intercept - intercept_d) * 3 - obs_near * 1.5
            # Tie-break deterministically by coordinates.
            s += -(rx * 0.01 + ry * 0.001)
            if s > move_score:
                move_score = s

        if move_score > best_move[1] or (move_score == best_move[1] and (dx, dy) < best_move[0]):
            best_move = ((dx, dy), move_score)

    return list(best_move[0])