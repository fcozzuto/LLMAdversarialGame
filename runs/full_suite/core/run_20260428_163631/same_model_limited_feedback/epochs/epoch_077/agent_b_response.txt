def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                moves.append((dx, dy, nx, ny))

    if not resources:
        tx, ty = clamp(ox, 0, w - 1), clamp(oy, 0, h - 1)
        best = None
        for dx, dy, nx, ny in moves:
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            sc = -d
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        if best:
            return [best[1], best[2]]
        return [0, 0]

    best_target = None
    best_adv = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        if best_target is None or adv > best_adv or (adv == best_adv and sd < dist((sx, sy), best_target)):
            best_target = (rx, ry)
            best_adv = adv

    # Predict opponent's likely next move toward their closest target, then avoid enabling them if possible.
    opp_target = None
    opp_best_d = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = dist((ox, oy), (rx, ry))
        if opp_best_d is None or d < opp_best_d:
            opp_best_d = d
            opp_target = (rx, ry)

    pred_opp = (ox, oy)
    if opp_target is not None:
        bestd = None
        for dx, dy, nx, ny in moves:
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), opp_target)
            if bestd is None or d < bestd:
                bestd = d
                pred_opp = (nx, ny)

    nx_best = None
    best_score = None
    for dx, dy, nx, ny in moves:
        if (nx, ny) in obstacles:
            continue
        self_d = dist((nx, ny), best_target)
        opp_d_after = dist(pred_opp, best_target)
        adv_after = opp_d_after - self_d
        block_bonus = 0
        if pred_opp == (nx, ny):
            block_bonus = -2  # avoid stepping into predicted opponent move
        score = adv_after * 10 - self_d + block_bonus
        if best_score is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            nx_best = (dx, dy)

    if nx_best is None:
        return [0, 0]
    return [nx_best[0], nx_best[1]]