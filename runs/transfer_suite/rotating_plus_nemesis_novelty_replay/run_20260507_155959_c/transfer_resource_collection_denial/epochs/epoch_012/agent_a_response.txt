def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        # fallback: drift toward center to avoid corners trap
        cx, cy = (w // 2), (h // 2)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -(md(nx, ny, cx, cy))
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Precompute opponent distances
    opp_d = {}
    for rx, ry in res:
        opp_d[(rx, ry)] = md(ox, oy, rx, ry)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0

        # immediate pickup dominance
        if (nx, ny) in opp_d:
            val += 100000

        # compute global advantage over all resources
        self_best = 10**9
        opp_best = 10**9
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = opp_d[(rx, ry)]
            if d_self < self_best:
                self_best = d_self
            if d_op < opp_best:
                opp_best = d_op

            adv = d_op - d_self  # positive means we are closer than opponent
            # prefer moves that create/expand advantage for nearer targets
            val += adv * 80
            val += -d_self * 2

        # strategic pressure: if we are currently behind overall, head to the best swing target
        swing = opp_best - self_best  # positive => we generally closer
        val += swing * 40

        # avoid moves that give the opponent immediate adjacent pickup if possible
        # (compute worst-case if opponent could step onto a resource next turn)
        opp_adj = []
        for pdx in (-1, 0, 1):
            for pdy in (-1, 0, 1):
                tx, ty = ox + pdx, oy + pdy
                if inb(tx, ty) and (tx, ty) not in obs and (tx, ty) in opp_d:
                    opp_adj.append((tx, ty))
        if opp_adj and (nx, ny) not in opp_d:
            val -= 3000

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]