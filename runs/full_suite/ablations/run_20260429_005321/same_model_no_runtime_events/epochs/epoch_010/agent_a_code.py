def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = (-1, 0, 1)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    def legal_moves():
        for dx in deltas:
            for dy in deltas:
                nx, ny = sx + dx, sy + dy
                if inside(nx, ny) and (nx, ny) not in obstacles:
                    yield dx, dy, nx, ny

    live_res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not live_res:
        # Move toward center while keeping away from opponent if possible
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = (0, 0)
        for dx, dy, nx, ny in legal_moves():
            k = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), dx, dy)
            if best is None or k < best:
                best = k
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    res_set = set(live_res)
    best_score = None
    best_move = (0, 0)

    for dx, dy, nx, ny in legal_moves():
        my_take = 1 if (nx, ny) in res_set else 0

        # Compute race advantage to best resource
        best_adv = -10**9
        worst_threat = 10**9
        close_bonus = 0
        for rx, ry in live_res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where I can arrive at least as fast (preferably sooner)
            adv = opd - myd
            if adv > best_adv:
                best_adv = adv

            # Threat if opponent can grab very soon while I can't
            if opd <= 1 and myd >= 2 and adv < 0:
                worst_threat = min(worst_threat, opd - myd)

            # Small bonus for closeness to any resource to avoid stagnation
            close_bonus = max(close_bonus, 6 - myd)

        # Avoid stepping onto an opponent-claimed resource next turn when possible
        # (approx: if opponent is adjacent to a resource and I'm far, reduce score)
        opp_adj_res = 0
        for rx, ry in live_res:
            if cheb(ox, oy, rx, ry) <= 1 and cheb(nx, ny, rx, ry) >= 2:
                opp_adj_res += 1
        opp_adj_pen = opp_adj_res * 2

        # Core score: take > win races > positional improvement
        # Higher is better.
        score = (my_take * 1000) + (best_adv * 20) + (close_bonus) - (opp_adj_pen) - cheb(nx, ny, ox, oy)

        # Tie-break deterministically: smallest resulting coordinate order
        if best_score is None or score > best_score or (score == best_score and (nx, ny, dx, dy) < (best_move[0], best_move[1], 0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]