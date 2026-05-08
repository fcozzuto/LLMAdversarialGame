def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list if p and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = [(c[0], c[1]) for c in unclaimed if c and len(c) >= 2]
    self_t = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []) if p and len(p) >= 2)
    opp_t = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []) if p and len(p) >= 2)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not targets:
        # build pseudo targets: cells adjacent to opponent territory or unclaimed if available
        frontier = set()
        for (x, y) in (opp_t or []):
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    if (nx, ny) not in opp_t:
                        frontier.add((nx, ny))
        targets = list(frontier)

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        # prefer claiming territory/unclaimed, pressure opponent-controlled cells
        base = 0
        if (x, y) in self_t:
            base += 0.6
        elif (x, y) in opp_t:
            base += 2.2  # likely flips control
        elif (x, y) not in obstacles:
            base += 2.0  # unclaimed

        if targets:
            # closeness to nearest target matters
            bestd = 10**9
            for tx, ty in targets[:20]:
                d = man(x, y, tx, ty)
                if d < bestd:
                    bestd = d
            base += 1.6 * (-bestd)
        # pressure: move away from our position less than opponent (deny/contest)
        d_opp_now = man(sx, sy, ox, oy)
        d_opp_next = man(x, y, ox, oy)
        base += 0.35 * (d_opp_now - d_opp_next)

        # slight penalty for moving into opponent territory if it also makes us far from targets
        if (x, y) in opp_t and targets:
            bestd2 = 10**9
            for tx, ty in targets[:20]:
                d = man(ox, oy, tx, ty)
                if d < bestd2:
                    bestd2 = d
            base -= 0.15 * (bestd2)

        return base

    best = [0, 0]
    bestv = -10**18
    # deterministic tie-break: fixed dir order; if equal, smaller (dx,dy) lexicographically after priority
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    return best