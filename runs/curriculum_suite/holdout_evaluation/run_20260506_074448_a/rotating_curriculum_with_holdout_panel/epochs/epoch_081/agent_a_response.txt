def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_res_for(posx, posy):
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = man(posx, posy, rx, ry)
            # tie-break: center preference
            cx, cy = (w - 1) // 2, (h - 1) // 2
            cent = abs(rx - cx) + abs(ry - cy)
            key = (d, cent, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    my_target = best_res_for(sx, sy)
    opp_target = best_res_for(ox, oy)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if my_target is None and opp_target is None:
        return [0, 0]
    if my_target is None:
        tx, ty = opp_target
    elif opp_target is None:
        tx, ty = my_target
    else:
        myd = man(sx, sy, my_target[0], my_target[1])
        oppd = man(ox, oy, my_target[0], my_target[1])
        od_my = man(sx, sy, opp_target[0], opp_target[1])
        od_opp = man(ox, oy, opp_target[0], opp_target[1])

        # Intercept bias: if we can reach their likely target no later, go there.
        if od_my <= od_opp:
            tx, ty = opp_target
        else:
            # Otherwise, pick resource maximizing our advantage, with slight anti-edge bias.
            def score(rx, ry):
                dme = man(sx, sy, rx, ry)
                dop = man(ox, oy, rx, ry)
                edge_bias = (abs(rx - cx) + abs(ry - cy))
                return (dop - dme, -edge_bias, -dme, rx, ry)
            best = my_target
            best_key = score(best[0], best[1])
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                k = score(rx, ry)
                if k > best_key:
                    best_key = k
                    best = (rx, ry)
            tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]
    return [0, 0]