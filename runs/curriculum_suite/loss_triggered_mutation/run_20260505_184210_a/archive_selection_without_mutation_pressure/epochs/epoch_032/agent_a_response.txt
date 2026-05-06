def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # If no resources, drift to center while staying safe.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move by evaluating the best resource we can reach and deny to opponent.
    # Deter opponent by adding pressure if opponent is much closer to any resource.
    best_move = legal[0]
    best_val = -10**9

    # Deterministically limit candidate resources to keep logic tight: closest-to-us first.
    res_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    cand = res_sorted[:6]

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Our best achievable lead (max of (opp_dist - self_dist) over candidates)
        our_lead = -10**9
        best_res = cand[0]
        for rx, ry in cand:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            if lead > our_lead or (lead == our_lead and (rx, ry) < (best_res[0], best_res[1])):
                our_lead = lead
                best_res = (rx, ry)

        # Denial term: if opponent is currently significantly closer to some resource,
        # move to reduce their distance more than it helps us.
        denial = 0
        for rx, ry in cand:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # When opponent is closer, penalize moves that don't bring us closer too.
            if do - ds > 0:
                pass
            else:
                denial -= (ds - do)

        # Tie-breaker: favor smaller distance to the best target.
        ds_best = cheb(nx, ny, best_res[0], best_res[1])

        val = our_lead * 100 + denial * 2 - ds_best
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]