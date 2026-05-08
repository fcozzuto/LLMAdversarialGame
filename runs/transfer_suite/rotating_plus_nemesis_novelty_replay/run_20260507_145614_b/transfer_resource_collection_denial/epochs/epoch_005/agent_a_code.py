def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]]

    turns = observation.get("turns_remaining", 0)
    maxd = 2 * (w + h) + 5

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = maxd
        opp_best = maxd
        best_adv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_best: my_best = myd
            if opd < opp_best: opp_best = opd
            # If we can arrive earlier than opponent, prioritize strongly; else deny by moving toward "contested" targets.
            adv = opd - myd
            arrive = myd
            slack = (turns - arrive) if turns is not None else 0
            w_adv = adv * 120 - myd * 3 + (slack if slack > 0 else -arrive)
            if adv > 0:
                w_adv += 500
            elif adv == 0:
                w_adv -= 80
            else:
                w_adv -= (abs(adv) * 40)
            # Slightly prefer fewer-step ties to reach some resource.
            if (rx, ry) == (nx, ny):
                w_adv += 10000
            if w_adv > best_adv:
                best_adv = w_adv
        # If no clear winning resource, still move to reduce distance to the opponent's nearest resource.
        denom = opp_best if opp_best < maxd else 1
        fallback = -my_best * 6 - (opp_best - my_best) * 2 - denom * 0.1
        score = best_adv + fallback
        cand = (score, -my_best, dx, dy)
        if cand > best:
            best = cand

    return [best[2], best[3]]