def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp = (ox, oy)
    self0 = (sx, sy)

    def best_self_score(selfp, oppp):
        best = -10**9
        for r in resources:
            sd = cheb(selfp, r)
            od = cheb(oppp, r)
            adv = od - sd  # positive => we are closer
            if adv > best:
                best = adv
        return best

    def best_opp_move(opp_p, selfp):
        best = -10**9
        best_m = (0, 0)
        for dx, dy in moves:
            nx, ny = opp_p[0] + dx, opp_p[1] + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = best_self_score(selfp, (nx, ny))  # we want to minimize this after we act
            opp_gain = -sc
            if opp_gain > best:
                best = opp_gain
                best_m = (dx, dy)
        return best_m

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        selfp = (nx, ny)
        odx, ody = best_opp_move(opp, selfp)
        oppp = (ox + odx, oy + ody)
        val = best_self_score(selfp, oppp)

        # Small tie-break: prefer moves that reduce our distance to the best resource for us
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]