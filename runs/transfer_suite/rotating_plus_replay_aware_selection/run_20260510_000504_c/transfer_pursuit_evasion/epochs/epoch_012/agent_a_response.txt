def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer_self = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    pursuer_opp = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = pursuer_self or (not pursuer_opp)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [None, None, -10**18]  # dx,dy,score

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for ddx, ddy in moves:
            if ddx == 0 and ddy == 0:
                continue
            nx, ny = x + ddx, y + ddy
            if valid(nx, ny):
                m += 1
        return m

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        if pursue:
            # minimize distance; prefer higher mobility to avoid getting boxed in
            score = -man * 100 + mob
        else:
            # maximize distance; prefer higher mobility as insurance
            score = man * 100 + mob
        # deterministic tie-break: lexicographic preference on (dx,dy) via small bias
        score += -(dx * 2 + dy) * 0.001
        if score > best[2]:
            best = [dx, dy, score]

    if best[0] is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]