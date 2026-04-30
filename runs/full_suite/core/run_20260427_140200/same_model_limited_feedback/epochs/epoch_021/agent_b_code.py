def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    my = observation["self_position"]
    op = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    x0, y0 = my
    ox, oy = op

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    myset = set(tuple(r) for r in resources)
    if (x0, y0) in myset:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            x, y = x0 + dx, y0 + dy
            if not inside(x, y) or (x, y) in obstacles:
                continue
            v = -dist((x, y), (ox, oy)) - 0.1 * dist((x, y), (cx, cy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Strategy shift: pick moves that maximize "time advantage" over opponent to the same target.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not inside(x, y) or (x, y) in obstacles:
            continue

        if (x, y) in myset:
            v = 1e9 - dist((x, y), (ox, oy))
        else:
            # For this candidate position, find the resource where we are closest earlier than opponent.
            best_adv = -10**18
            p = (x, y)
            for r in resources:
                adv = dist((ox, oy), r) - dist(p, r)
                if adv > best_adv:
                    best_adv = adv
            # Extra shaping: prefer resources that are closer overall if tied, and avoid immediate conflict.
            mind = min(dist((x, y), r) for r in resources)
            conflict = 1.0 / (1 + dist((x, y), (ox, oy)))
            v = best_adv - 0.15 * mind - 2.5 * conflict
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]