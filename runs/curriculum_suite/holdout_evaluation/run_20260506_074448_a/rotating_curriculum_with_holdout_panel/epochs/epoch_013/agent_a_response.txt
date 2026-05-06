def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_opponent_step(cx, cy):
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # opponent greedy: minimize distance to nearest resource; tie-break toward increasing x,y
            md = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = cheb(nx, ny, rx, ry)
                if d < md:
                    md = d
            key = (md, -nx, -ny, 0)
            if key < best:
                best = key
        # if all blocked, stay
        return best[2], best[3] if best[2] or best[3] else (0, 0)

    odx, ody = best_opponent_step(ox, oy)
    nox, noy = ox + odx, oy + ody

    best_move = (None, -10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # advantage: maximize (my best proximity) - (opp best proximity) over contested resources
        my_dmin = 10**9
        opp_dmin = 10**9
        my_closest = None
        opp_closest = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dm = cheb(nx, ny, rx, ry)
            do = cheb(nox, noy, rx, ry)
            if dm < my_dmin:
                my_dmin = dm
                my_closest = (rx, ry)
            if do < opp_dmin:
                opp_dmin = do
                opp_closest = (rx, ry)

        # We want to reduce our distance while keeping at least one resource closer than opponent.
        advantage = opp_dmin - my_dmin

        # Tie-break: prefer being closer to a resource that is also near opponent (interception),
        # then prefer interior to avoid edge stalls.
        intercept_bonus = 0
        if my_closest and opp_closest and my_closest == opp_closest:
            intercept_bonus = 2
        # interior preference
        d_edge = min(nx, w - 1 - nx, ny, h - 1 - ny)

        key_adv = advantage + intercept_bonus
        key = (key_adv, d_edge, -my_dmin)
        if best_move[0] is None or key > (best_move[1], best_move[2], best_move[2]):
            best_move = ([dx, dy], key_adv, -my_dmin)

    if best_move[0] is None:
        return [0, 0]
    return best_move[0]