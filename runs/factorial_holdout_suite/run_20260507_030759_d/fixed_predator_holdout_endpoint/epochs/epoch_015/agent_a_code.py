def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def cheb(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da if da > db else db

    if not resources:
        tx, ty = w - 1, h - 1
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # Deterministic scoring: maximize our immediate advantage; break ties by prioritizing reachability.
    def step_score(nx, ny):
        best_adv = -10**9
        best_reach = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d  # positive means we're closer
            if adv > best_adv:
                best_adv = adv
                best_reach = my_d
            elif adv == best_adv and my_d < best_reach:
                best_reach = my_d
        # If we're not advantaged anywhere, try to reduce opponent's best advantage
        opp_best = -10**9
        for rx, ry in resources:
            opp_best = max(opp_best, cheb(sx, sy, rx, ry) - cheb(ox, oy, rx, ry))
        return (best_adv, -best_reach, -opp_best)

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        sc = step_score(nx, ny)
        cand = (sc, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[1], best[2]]