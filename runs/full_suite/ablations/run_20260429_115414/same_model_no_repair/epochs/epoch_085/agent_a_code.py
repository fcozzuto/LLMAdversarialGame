def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = {(p[0], p[1]) for p in obstacles}

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_r = None
    best_adv = None
    for rx, ry in resources:
        myd = cheb((sx, sy), (rx, ry))
        opd = cheb((ox, oy), (rx, ry))
        adv = (opd - myd)  # want ours smaller => adv positive
        # tie-break: choose nearer resource among those with same adv
        if best_adv is None or adv > best_adv or (adv == best_adv and myd < cheb((sx, sy), best_r)):
            best_adv = adv
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        myd = cheb((nx, ny), (tx, ty))
        opd = cheb((ox, oy), (tx, ty))
        score = (opd - myd) * 100 - myd  # strongly prioritize winning the race to target
        # secondary: if we aren't racing well, prefer moves that improve advantage to any resource
        if score < 0:
            best_any = -10**9
            for rx, ry in resources:
                a = (cheb((ox, oy), (rx, ry)) - cheb((nx, ny), (rx, ry)))
                if a > best_any:
                    best_any = a
            score = score + best_any
        # tie-break: avoid moving away from current target and avoid increasing distance to closest resource
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cur_closest = min(cheb((sx, sy), r) for r in resources)
            new_closest = min(cheb((nx, ny), r) for r in resources)
            if new_closest < cur_closest:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]