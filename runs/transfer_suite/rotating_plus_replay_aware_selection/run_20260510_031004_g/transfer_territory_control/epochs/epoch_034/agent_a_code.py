def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax if ax >= ay else ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a few promising unclaimed targets near us; reward targets we can reach sooner than opponent.
    targets = []
    if unclaimed:
        unclaimed.sort(key=lambda t: cheb(sx, sy, t[0], t[1]))
        targets = unclaimed[:12]

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 260
        if (nx, ny) in opp_terr:
            val += 140
        if (nx, ny) in self_terr:
            val += 30
        if (nx, ny) == (sx, sy):
            val -= 5

        # Contest: choose moves that put us in range of targets where we are closer than the opponent.
        if targets:
            tbest = -10**18
            for tx, ty in targets:
                # Prefer moving so that next step is not too slow to the target compared to opponent.
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(px, py, tx, ty)
                lead = opd - myd  # positive if we are closer
                tscore = 70 * lead - 3 * myd
                # Strongly prefer direct entry to the target if possible in one step.
                if (nx, ny) == (tx, ty):
                    tscore += 250
                if tscore > tbest:
                    tbest = tscore
            val += tbest
        else:
            # No unclaimed: keep pressuring toward center and opponent boundary.
            cx, cy = w // 2, h // 2
            val += 2 * (-cheb(nx, ny, cx, cy))
            val += 18 * (-cheb(nx, ny, px, py))

        # Avoid getting stuck behind obstacles: slight penalty for increasing distance to nearest unclaimed.
        if unclaimed:
            ux, uy = min(unclaimed, key=lambda t: cheb(sx, sy, t[0], t[1]))
            d0 = cheb(sx, sy, ux, uy)
            d1 = cheb(nx, ny, ux, uy)
            if d1 > d0:
                val -= 10 * (d1 - d0)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]