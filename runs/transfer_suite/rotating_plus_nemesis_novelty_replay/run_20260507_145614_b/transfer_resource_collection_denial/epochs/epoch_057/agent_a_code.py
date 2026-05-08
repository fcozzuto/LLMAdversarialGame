def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return [0 if sx == tx else (1 if tx > sx else -1), 0 if sy == ty else (1 if ty > sy else -1)]

    if (sx, sy) in [tuple(r) for r in resources]:
        return [0, 0]

    def d(ax, ay, bx, by):
        ddx = ax - bx; ddx = ddx if ddx >= 0 else -ddx
        ddy = ay - by; ddy = ddy if ddy >= 0 else -ddy
        return ddx if ddx > ddy else ddy

    # one-step lookahead: choose move maximizing advantage to best target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # pick best target for this next position
        chosen = None
        chosen_val = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            sd = d(nx, ny, rx, ry)
            od = d(ox, oy, rx, ry)
            # advantage: be closer than opponent; also avoid easy row contest by biasing different y
            adv = (od - sd) * 100 - abs(ry - oy)
            # slight preference for nearer targets to reduce time to collection
            adv -= sd
            if adv > chosen_val:
                chosen_val = adv
                chosen = (rx, ry)
        # prefer immediate capture if possible
        if chosen and chosen == (nx, ny):
            val = 10**12
        else:
            # also penalize moving toward opponent's y significantly (to reduce sweep-row interference)
            rx, ry = chosen
            val = chosen_val - abs(ny - oy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]