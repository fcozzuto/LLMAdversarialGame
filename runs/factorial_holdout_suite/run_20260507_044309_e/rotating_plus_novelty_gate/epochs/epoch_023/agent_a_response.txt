def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    valid = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry):
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    # Immediate grab if adjacent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        for rx, ry in valid:
            if nx == rx and ny == ry:
                return [dx, dy]

    best_move = [0, 0]
    best_score = -10**18
    best_self_dist = 10**9

    # Prefer moves that secure some resource before opponent; otherwise go toward fastest contested/resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        local_best = -10**18
        local_self_best = 10**9
        for rx, ry in valid:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer winning (sd < od), then bigger advantage; slight preference for closer wins.
            advantage = od - sd
            win_bonus = 10000 if sd <= od else 0
            time_weight = (turns_remaining + 1) - sd
            score = win_bonus + advantage * 20 + time_weight
            if score > local_best or (score == local_best and sd < local_self_best):
                local_best = score
                local_self_best = sd
        if local_best > best_score or (local_best == best_score and local_self_best < best_self_dist):
            best_score = local_best
            best_self_dist = local_self_best
            best_move = [dx, dy]

    return best_move