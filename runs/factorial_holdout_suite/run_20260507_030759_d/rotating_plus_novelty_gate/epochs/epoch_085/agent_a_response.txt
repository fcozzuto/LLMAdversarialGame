def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def legal_moves(pos):
        x, y = pos
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    out.append((dx, dy))
        return out if out else [(0, 0)]

    my_moves = legal_moves((sx, sy))
    if not res:
        return [0, 0]

    # Opponent greedy-next assumption: move to minimize distance to the nearest resource.
    opp_legal = legal_moves((ox, oy))
    if res:
        def opp_target_and_bestcell():
            bestd = None
            best = None
            for r in res:
                d = md((ox, oy), r)
                if bestd is None or d < bestd or (d == bestd and r < best):
                    bestd, best = d, r
            return best
        opp_target = opp_target_and_bestcell()
    else:
        opp_target = (ox, oy)

    def greedy_opp_next():
        best = None
        for dx, dy in opp_legal:
            nx, ny = ox + dx, oy + dy
            d = md((nx, ny), opp_target)
            cand = (d, nx, ny)
            if best is None or cand < best:
                best = cand
        return (best[1], best[2])

    opp_next = greedy_opp_next()

    # Evaluate our candidate moves by how many resources we are predicted to reach first (tie favors us).
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in my_moves:
        nx, ny = sx + dx, sy + dy
        lead = 0
        best_my = None
        best_margin = None
        for r in res:
            d_my = md((nx, ny), r)
            d_opp = md(opp_next, r)
            if d_my <= d_opp:
                lead += 1
                m = d_opp - d_my
                if best_my is None or d_my < best_my or (d_my == best_my and m > (best_margin if best_margin is not None else -10**9)):
                    best_my = d_my
                    best_margin = m
        # Prefer more leads, then closer best lead, then larger margin; deterministic tie-break by move order.
        cand_tuple = (lead, -(best_margin if best_margin is not None else -10**9), -(best_my if best_my is not None else 10**9), dx, dy)
        if best_tuple is None or cand_tuple > best_tuple:
            best_tuple = cand_tuple
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]