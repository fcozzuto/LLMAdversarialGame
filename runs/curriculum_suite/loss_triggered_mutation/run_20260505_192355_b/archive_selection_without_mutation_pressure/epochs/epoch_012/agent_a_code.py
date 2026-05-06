def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    legal_moves = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]
    if not legal_moves:
        return [0, 0]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    def edge_bonus(x, y):
        d = x
        if w - 1 - x < d: d = w - 1 - x
        if y < d: d = y
        if h - 1 - y < d: d = h - 1 - y
        return 3 if d == 0 else (2 if d == 1 else 0)
    if not resources:
        best = legal_moves[0]; bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, ox, oy) + edge_bonus(nx, ny)
            if v > bestv: bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Predict opponent greedy move towards nearest resource (deterministic).
    def opp_greedy(px, py):
        best = (0, 0); bestv = -10**18
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny): 
                continue
            # prefer nearer to closest resource, slight preference to edges to avoid being trapped
            myd = min(man(nx, ny, rx, ry) for rx, ry in resources)
            v = -myd + 0.1 * edge_bonus(nx, ny)
            if v > bestv: bestv, best = v, (dx, dy)
        return best

    odx, ody = opp_greedy(ox, oy)
    pnx, pny = ox + odx, oy + ody

    best = legal_moves[0]; bestv = -10**18
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        # Contest each resource: we want resources where opponent is later (or never beats us).
        # Also keep overall progress towards reachable resources.
        my_best = 10**9
        opp_best_if_contest = 0
        # max lead = my turn-advantage
        max_lead = -10**9
        min_time = 10**9
        for rx, ry in resources:
            dme = man(nx, ny, rx, ry)
            dome = man(pnx, pny, rx, ry)
            if dme < my_best: my_best = dme
            if dome < min_time: min_time = dome
            lead = dome - dme  # positive means we are closer
            if lead > max_lead: max_lead = lead
            if dome <= dme:
                # heavily penalize resources opponent can match/beat; encourages denial behavior.
                opp_best_if_contest -= 6 * (dme - dome + 1)
            else:
                opp_best_if_contest += 2 * lead
        v = 5 * max_lead - my_best + 0.5 * edge_bonus(nx, ny) + opp_best_if_contest
        # Prefer moves that increase distance from opponent when contest is tight.
        v -= 0.01 * man(nx, ny, pnx, pny)
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]