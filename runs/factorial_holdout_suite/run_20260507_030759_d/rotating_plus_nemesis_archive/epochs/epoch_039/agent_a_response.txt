def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if (sx, sy) in obst:
        return [0, 0]
    if not res:
        return [0, 0]

    if (sx, sy) in res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        my = (nx, ny)

        # Score: how much closer we are than opponent to the best collectible.
        # If equal, prefer smaller sum distance (faster pickup).
        cur_best = -10**18
        for rx, ry in res:
            r = (rx, ry)
            myd = man(my, r)
            opd = man((ox, oy), r)
            advantage = opd - myd  # positive means we are closer
            score = advantage * 100 - (myd * 2) - (opd)
            if score > cur_best:
                cur_best = score

        # Small tie-break: avoid moving away from the overall nearest resource.
        nearest = min(man((sx, sy), rr) for rr in res)
        nearest_after = min(man((nx, ny), rr) for rr in res)
        cur_best -= (nearest_after - nearest)

        if cur_best > best_score:
            best_score = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]