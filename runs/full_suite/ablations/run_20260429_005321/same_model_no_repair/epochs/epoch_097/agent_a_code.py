def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        for rx, ry in resources:
            if sx == rx and sy == ry:
                return [0, 0]

    # Obstacle proximity penalty (deterministic, local)
    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    adj_diag = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    def local_pen(x, y):
        p = 0
        for ddx, ddy in adj4:
            if (x + ddx, y + ddy) in obst:
                p += 2
        for ddx, ddy in adj_diag:
            if (x + ddx, y + ddy) in obst:
                p += 1
        return p

    # Choose move maximizing worst-case (me being earlier) over resources,
    # with tie-breakers towards closer resources and away from opponent.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        lp = local_pen(nx, ny)
        if resources:
            my_best = 10**9
            opp_best = 10**9
            advantage = -10**9
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                my_best = md if md < my_best else my_best
                opp_best = od if od < opp_best else opp_best
                # prefer being strictly closer; if equal, slightly prefer farther opponent
                a = (od - md) * 10 - (1 if od == md else 0)
                if a > advantage:
                    advantage = a
            # primary: advantage, secondary: reduce my_best, tertiary: increase opp_best, final: minimize local penalty
            v = advantage - 2 * my_best + 0.5 * opp_best - lp
        else:
            # no resources: drift towards center while keeping distance from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dcent = abs(nx - cx) + abs(ny - cy)
            distopp = cheb(nx, ny, ox, oy)
            v = -dcent + 0.05 * distopp - lp

        # deterministic tie-break: prefer smaller (dx,dy) lexicographically
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]