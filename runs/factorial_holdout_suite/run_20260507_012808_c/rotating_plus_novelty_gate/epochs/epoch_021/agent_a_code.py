def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    res = [tuple(p) for p in resources]
    if not res:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        self_on = 1 if (nx, ny) in obstacles else 0  # never true, keeps deterministic structure
        step_pick = 1 if (nx, ny) in res else 0

        myd_to_best = 10**9
        target_adv = -10**18

        for r in res:
            myd = cd((nx, ny), r)
            opd = cd((ox, oy), r)
            # prefer immediate pickup, then states that leave opponent behind and reduce own distance
            adv = (opd - myd)
            val = adv * 80 + (160 - myd) - max(0, myd - opd) * 25
            if val > target_adv:
                target_adv = val
                myd_to_best = myd

        # Encourage moving toward nearer resources (especially when opponent is not winning)
        opp_close = min(cd((ox, oy), r) for r in res)
        own_close = min(cd((nx, ny), r) for r in res)
        opp_factor = (opp_close - own_close)

        score = step_pick * 100000 + target_adv + opp_factor * 10 - myd_to_best * 1
        if score > best_score or (score == best_score and (mx, my) < best):
            best_score = score
            best = (mx, my)

    return [best[0], best[1]]