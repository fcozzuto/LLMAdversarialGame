def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Predict opponent's current target by nearest resource to opponent.
    opp_best = None
    opp_bd = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        if d < opp_bd or (d == opp_bd and (rx, ry) < opp_best):
            opp_bd = d
            opp_best = (rx, ry)
    if opp_best is None:
        return [0, 0]
    tx, ty = opp_best

    myd_to_opp = man(sx, sy, tx, ty)
    od_to_opp = man(ox, oy, tx, ty)

    # Choose a response target:
    # 1) If we can beat/tie on opponent's predicted target, go there.
    # 2) Else, go for the closest resource we can reach strictly before them.
    # 3) Else, just go for our closest reachable resource.
    best = None
    best_key = None
    if myd_to_opp <= od_to_opp:
        best = (tx, ty)
    else:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            if myd < od:
                key = (myd, rx, ry)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (rx, ry)
        if best is None:
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = man(sx, sy, rx, ry)
                key = (myd, rx, ry)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (rx, ry)

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Deterministic obstacle-avoidance by trying preferred deltas toward the target.
    candidates = [
        (dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy),
        (0, 0), (-dx, 0), (0, -dy), (-dx, -dy)
    ]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    return [0, 0]