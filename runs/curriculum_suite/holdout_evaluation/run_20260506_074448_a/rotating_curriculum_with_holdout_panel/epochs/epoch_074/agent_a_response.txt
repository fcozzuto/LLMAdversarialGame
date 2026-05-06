def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []; obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    opp_nearest = None; opp_nearest_d = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        d = man(ox, oy, rx, ry)
        if opp_nearest is None or d < opp_nearest_d or (d == opp_nearest_d and (rx, ry) < opp_nearest):
            opp_nearest = (rx, ry); opp_nearest_d = d

    my_best = None; my_key = None
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry); oppd = man(ox, oy, rx, ry)
        tempo_adv = oppd - myd
        cent = abs(rx - cx) + abs(ry - cy)
        key = (-tempo_adv, cent, myd, rx, ry)
        if my_key is None or key < my_key:
            my_key = key; my_best = (rx, ry)

    if my_best is None and opp_nearest is None:
        return [0, 0]

    tx1, ty1 = my_best if my_best is not None else (sx, sy)
    tx2, ty2 = opp_nearest if opp_nearest is not None else (sx, sy)

    best = None; best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = man(nx, ny, tx1, ty1)
        d2 = man(nx, ny, tx2, ty2)
        myd1 = man(sx, sy, tx1, ty1); oppd1 = man(ox, oy, tx1, ty1)
        myd2 = man(sx, sy, tx2, ty2); oppd2 = man(ox, oy, tx2, ty2)
        adv1 = (oppd1 - d1)
        adv2 = (oppd2 - d2)
        cent = abs(nx - cx) + abs(ny - cy)
        # Prefer securing our best resource, but also contest opponent's likely nearest.
        score = (10 * adv1) + (3 * adv2) - (0.4 * d1) - (0.15 * cent) - (0.05 * d2) + (0.2 * (myd1 - d1) if d1 <= myd1 else -0.1)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]