def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    target_op = min(resources, key=lambda p: man(ox, oy, p[0], p[1]))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set((p[0], p[1]) for p in resources)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            return [dx, dy]

        move_score = -10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            gain = d_opp - d_self  # positive means we are closer

            # Avoid the opponent's most likely immediate focus
            if (rx, ry) == (target_op[0], target_op[1]):
                gain -= 8

            # If we can win this resource (strictly closer), reward it heavily
            if gain > 0:
                gain += 20

            # Prefer reducing our distance even when race is unclear
            gain -= (d_self * 0.5)

            # Discourage paths that would let opponent be closer by a lot
            if d_opp < d_self:
                gain -= 3 * (d_self - d_opp)

            if gain > move_score:
                move_score = gain

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]