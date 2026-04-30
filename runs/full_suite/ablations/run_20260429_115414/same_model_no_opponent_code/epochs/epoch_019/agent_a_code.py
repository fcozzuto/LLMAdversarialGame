def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
        except:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
        except:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))

    if (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if res:
        res_set = set(res)
        def man_dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

        opp_best = min(man_dist((ox, oy), r) for r in res)
        best_move, best_score = [0, 0], -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            if (nx, ny) in res_set:
                return [dx, dy]
            my_best = min(man_dist((nx, ny), r) for r in res)
            score = (-my_best) + 0.5 * (opp_best) - 0.01 * my_best
            if score > best_score:
                best_score, best_move = score, [dx, dy]
        return best_move

    # No resources: move away from opponent
    best_move, best_score = [0, 0], -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score, best_move = score, [dx, dy]
    return best_move if legal(sx + best_move[0], sy + best_move[1]) else [0, 0]