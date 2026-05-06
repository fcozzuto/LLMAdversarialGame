def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Defensive: move toward midpoint but also away from opponent direction a bit
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = (man(nx, ny, tx, ty), man(nx, ny, ox, oy), dx, dy)
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Offensive/interception: maximize immediate advantage over the opponent for the best target resource
    best = (0, 0)
    bestv = None
    for dx, dy, nx, ny in moves:
        # Find the best resource to "out-race"
        local_best_adv = -10**9
        local_best_d = 10**9
        local_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_d):
                local_best_adv, local_best_d = adv, sd
                local_best = (rx, ry, sd, od, adv)

        rx, ry, sd, od, adv = local_best

        # If we can out-race (adv>0), strongly prefer that and closer progress; else, intercept nearest resource
        if adv > 0:
            v = (-adv, sd, -od, dx, dy)
        else:
            # Interception fallback: go toward the nearest resource to opponent (so we pressure their path)
            opp_nearest = None
            opp_nd = 10**9
            for r2x, r2y in resources:
                t = man(ox, oy, r2x, r2y)
                if t < opp_nd:
                    opp_nd, opp_nearest = t, (r2x, r2y)
            px, py = opp_nearest
            v = (adv, man(nx, ny, px, py), -man(nx, ny, rx, ry), dx, dy)

        if bestv is None or v < bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]