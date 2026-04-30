def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs = set((x, y) for x, y in obstacles)
    res = [(x, y) for x, y in resources if 0 <= x < w and 0 <= y < h and (x, y) not in obs]
    if not res:
        # No resources visible: move to reduce distance to opponent (likely to contest)
        dxs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (10**9, 0, 0)
        for dx, dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource where we can arrive significantly earlier than opponent.
    best_r = None
    best_adv = -10**9
    for r in res:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = do - ds  # higher is better: we are closer/equal than opponent
        # small bias to closer overall to avoid far dead-ends
        adv -= 0.05 * ds
        if adv > best_adv:
            best_adv = adv
            best_r = r
        elif adv == best_adv and best_r is not None:
            # tie-break: prefer resources closer to us
            if ds < dist((sx, sy), best_r):
                best_r = r

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # If the opponent is about to take the same resource, try to intercept by aiming at a step that
    # also reduces opponent's distance to that resource.
    intercept_weight = 1.0 if best_adv <= 0 else 0.25

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        ds1 = dist((nx, ny), (tx, ty))
        do1 = dist((ox, oy), (tx, ty))
        # Our progress toward target + contesting pressure if we can't be first.
        progress = -ds1
        contest = -abs(do1 - ds1)
        # Also slightly avoid stepping into squares closer to opponent if target is contested.
        opp_close_pen = -dist((nx, ny), (ox, oy)) * (0.05 if best_adv <= 0 else 0.0)
        score = 1.2 * progress + intercept_weight * contest + opp_close_pen

        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            # deterministic tie-break: prefer moves that reduce distance to target, then lexicographic
            cur_d = ds1
            best_d = dist((sx + best[1], sy + best[2]), (tx, ty))
            if cur_d < best_d or (cur_d == best_d and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]