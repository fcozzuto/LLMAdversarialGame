def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set(map(lambda p: (p[0], p[1]), obstacles_raw))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = [0, 0]
    best_score = -10**18

    if not res:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = abs(nx - ox) + abs(ny - oy)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1

        dO = abs(nx - ox) + abs(ny - oy)
        score = -2 * adj_obs - 0.1 * dO
        # prefer being closer than opponent to a resource
        for rx, ry in res:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            value = opd - myd
            # small tie-breaker: closer objective overall
            value -= 0.01 * myd
            if value > score:
                score = value

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move