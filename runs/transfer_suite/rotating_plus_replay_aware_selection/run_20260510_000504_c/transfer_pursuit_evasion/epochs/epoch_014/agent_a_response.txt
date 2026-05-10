def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            if valid(x + dx, y + dy):
                m += 1
        return m

    def near_obs(x, y):
        # lower is better for pursuer (avoid clutter), higher is better for evader (prefer open)
        d = 10
        for oxp, oyp in obstacles:
            dd = abs(x - oxp) + abs(y - oyp)
            if dd < d:
                d = dd
        return d if obstacles else 9

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer_self = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    pursuer_opp = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = pursuer_self or (not pursuer_opp)

    best_dxdy = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        dn = near_obs(nx, ny)
        # Deterministic composite score:
        # - if pursuing: prefer smaller distance, then higher mobility, then farther from obstacles
        # - if evading: prefer larger distance, then higher mobility, then farther from obstacles
        if pursue:
            score = -dist * 1000 + mob * 10 + dn
        else:
            score = dist * 1000 + mob * 10 + dn
        if score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]