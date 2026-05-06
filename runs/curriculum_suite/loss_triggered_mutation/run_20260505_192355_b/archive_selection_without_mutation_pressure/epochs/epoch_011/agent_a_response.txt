def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    legal_moves = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]
    if not legal_moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = legal_moves[0]
        bestv = -10**9
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, ox, oy)  # drift away from opponent when empty
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best = legal_moves[0]
    bestv = -10**18
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        my_min = 10**9
        opp_min = 10**9
        beat_margin = 10**9  # how much I can beat opponent on best race
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        edge = edge if edge < 2 else 0

        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if dm < my_min:
                my_min = dm
            if do < opp_min:
                opp_min = do
            margin = do - dm  # positive means I reach earlier than opponent (race)
            if margin < beat_margin:
                beat_margin = margin  # pessimistic (focus on securing at least one race reliably)

        # Main objective: prioritize moves that improve my nearest pickup while also
        # maximizing the worst "can I beat the opponent" margin.
        v = (-my_min) + 1.8 * beat_margin + 0.15 * (opp_min - my_min) + 0.5 * edge

        # Secondary tie-breaker: avoid stepping into squares adjacent to obstacles (deterministic)
        if v == bestv:
            ob_adj = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in obstacles:
                    ob_adj += 1
            bdx, bdy = best
            bnx, bny = sx + bdx, sy + bdy
            ob_adj_best = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                tx, ty = bnx + adx, bny + ady
                if (tx, ty) in obstacles:
                    ob_adj_best += 1
            if ob_adj < ob_adj_best:
                best, bestv = (dx, dy), v
        elif v > bestv:
            best, bestv = (dx, dy), v

    return [best[0], best[1]]