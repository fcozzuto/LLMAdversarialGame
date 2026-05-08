def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    rset = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in rset:
            return [dx, dy]

    best = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = (nx, ny)

        # Race metric: for each resource, prefer where opponent is farther and where we can "secure" it.
        local_best = -10**18
        for tr in rset:
            sd = man(ns, tr)
            od = man((ox, oy), tr)
            # Prefer resources we can reach earlier; break ties by larger gap and shorter self distance.
            # A small penalty discourages very long trips that can lose to alternatives.
            gap = od - sd
            secure = 1 if sd <= od else 0
            val = (secure * 10**6) + gap * 1000 - sd
            if val > local_best:
                local_best = val

        # Small extra bias to reduce distance to opponent's nearest resource (force conflict).
        opp_target = min(rset, key=lambda r: man((ox, oy), r))
        opp_dist = man(opp_target, (nx, ny))
        local_best += -opp_dist * 2

        if local_best > best_val:
            best_val = local_best
            best = [dx, dy]

    return [int(best[0]), int(best[1])]