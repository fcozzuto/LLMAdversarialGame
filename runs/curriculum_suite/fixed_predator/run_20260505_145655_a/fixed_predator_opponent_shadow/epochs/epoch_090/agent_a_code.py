def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Pick best resource for advantage; if too contested, pick second-best.
    best = None
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me + 0.001 * d_opp
        if best_tv is None or tv > best_tv or (tv == best_tv and (tx, ty) < (best[0], best[1])):
            best = r
            best_tv = tv
    target = best

    tx, ty = target[0], target[1]
    d_me = abs(tx - x) + abs(ty - y)
    d_opp = abs(tx - ox) + abs(ty - oy)

    if d_opp <= d_me:
        # Find a less contested (or still advantaged) resource.
        alt = None
        alt_tv = None
        for r in resources:
            t2x, t2y = r[0], r[1]
            dm2 = abs(t2x - x) + abs(t2y - y)
            do2 = abs(t2x - ox) + abs(t2y - oy)
            tv2 = (do2 - dm2) * 1000 - dm2 + 0.001 * do2
            if alt_tv is None or tv2 > alt_tv or (tv2 == alt_tv and (t2x, t2y) < (alt[0], alt[1])):
                alt = r
                alt_tv = tv2
        target = alt
        tx, ty = target[0], target[1]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        my_new = abs(tx - nx) + abs(ty - ny)
        opp_new = abs(tx - ox) + abs(ty - oy)
        # If opponent is about to capture this resource, prefer moving toward a better one.
        # Approximate by using best immediate advantage over all resources.
        best_adv = None
        for r in resources:
            t2x, t2y = r[0], r[1]
            dm = abs(t2x - nx) + abs(t2y - ny)
            do = abs(t2x - ox) + abs(t2y - oy)
            adv = (do - dm) * 1000 - dm + 0.001 * do
            if best_adv is None or adv > best_adv:
                best_adv = adv
        score = (opp_new - my_new) * 1000 - my_new + 0.0001 * best_adv
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]