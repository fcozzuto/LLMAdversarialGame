def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx = 0
        ty = 0
    else:
        best = None
        for rx, ry in resources:
            d_self = abs(rx - sx) + abs(ry - sy)
            d_opp = abs(rx - ox) + abs(ry - oy)
            # advantage score: want resources we can get sooner; break ties by closeness
            score = (d_opp - d_self) * 10 - d_self
            key = (score, -rx, -ry)  # deterministic
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # primary: move toward chosen target
        d_t = abs(tx - nx) + abs(ty - ny)
        # secondary: reduce opponent proximity to our target region
        d_t_opp = abs(tx - ox) + abs(ty - oy)
        opp_push = abs(tx - ox) - abs(tx - ox - (1 if ox < tx else -1 if ox > tx else 0))  # small deterministic proxy
        # global: if resources exist, pick move maximizing future advantage on best reachable resource
        adv = 0
        if resources:
            adv_best = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                our = abs(rx - nx) + abs(ry - ny)
                opp = abs(rx - ox) + abs(ry - oy)
                s = (opp - our) * 10 - our
                if s > adv_best:
                    adv_best = s
            adv = adv_best
        val = (adv, -d_t, opp_push, -(abs(nx - ox) + abs(ny - oy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move