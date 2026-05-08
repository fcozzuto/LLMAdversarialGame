def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_t.add((p[0], p[1]))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_t.add((p[0], p[1]))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return -10**9
        if (x, y) in self_t:
            base = 1.0
        elif (x, y) in opp_t:
            base = 12.0
        elif (x, y) in unclaimed:
            base = 6.5
        else:
            base = 3.0
        d = abs(x - ox) + abs(y - oy)
        adv = -0.35 * d
        # If stepping into a boundary region, prefer it
        neigh_opp = 0
        neigh_un = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                if (nx, ny) in opp_t:
                    neigh_opp += 1
                if (nx, ny) in unclaimed:
                    neigh_un += 1
        boundary = 1.6 * neigh_opp + 0.8 * neigh_un
        # Slight bias to stay within our currently controlled front (minimize moving away)
        d0 = abs(sx - ox) + abs(sy - oy)
        adv2 = 0.25 * (d0 - d)
        return base + adv + boundary + adv2

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        sc = cell_score(x, y)
        # Deterministic tie-breaker: earlier dirs preferred, then closer to opponent, then smaller dx/dy
        if sc > best[0] or (sc == best[0] and (abs(x - ox) + abs(y - oy), dx, dy) < (abs(best[1] - ox) + abs(best[2] - oy), best[1], best[2])):
            best = (sc, x, y)
            best_move = [dx, dy]

    return best_move