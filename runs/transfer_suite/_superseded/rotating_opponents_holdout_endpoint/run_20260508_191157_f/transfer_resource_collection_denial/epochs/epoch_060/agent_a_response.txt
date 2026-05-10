def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]
    res_set = set(tuple(p) for p in resources)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            gap = do - ds  # positive means we are closer
            hit = 1 if (nx, ny) == (rx, ry) else 0
            score = hit * 10000 + gap * 60 - ds
            if score > local_best:
                local_best = score

        if local_best > best_score:
            best_score = local_best
            best_move = [dx, dy]

    # If all moves invalid (unlikely), stay put
    return best_move