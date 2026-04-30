def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is None:
            continue
        obstacles.add((p[0], p[1]))
    resources = observation.get("resources") or []

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # chase opponent
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            val = -man(nx, ny, ox, oy)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # pick move that maximizes advantage over opponent for the best reachable resource
    best_move = (0, 0)
    best_adv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        best_for_this = -10**18
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # higher means I can get there sooner / better
            adv = opd - myd
            # small tie-breakers: prefer closer to resource and discourage far moves
            adv = adv * 10000 - myd
            if adv > best_for_this:
                best_for_this = adv
        if best_for_this > best_adv or (best_for_this == best_adv and (dx, dy) < best_move):
            best_adv = best_for_this
            best_move = (dx, dy)

    if best_move == (0, 0):
        # fallback: take any valid move
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            return [dx, dy]
    return [best_move[0], best_move[1]]