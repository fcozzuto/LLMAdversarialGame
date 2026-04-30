def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    def dist(a, b, c, d):
        da = a - c
        db = b - d
        if da < 0: da = -da
        if db < 0: db = -db
        return da if da > db else db

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 10**9)
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, cx, cy)
            tup = (d, dx, dy)
            if tup < best:
                best = tup
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Deterministic tie-breaking by (dx,dy) order
    best = (10**9, 10**9, 10**9)
    best_move = (0, 0)

    # Opponent distances to each resource (static for this move)
    opp_ds = []
    for rx, ry in resources:
        opp_ds.append(dist(ox, oy, rx, ry))

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best_gap = 10**9
        my_min_dist = 10**9
        for i, (rx, ry) in enumerate(resources):
            md = dist(nx, ny, rx, ry)
            od = opp_ds[i]
            gap = md - od  # prefer md < od (negative), i.e., I can reach sooner than opponent
            if gap < my_best_gap:
                my_best_gap = gap
            if md < my_min_dist:
                my_min_dist = md

        # Small penalty for stepping adjacent to obstacles to avoid deterministic traps
        adj_pen = 0
        for adx, ady in dirs:
            ax2, ay2 = nx + adx, ny + ady
            if inb(ax2, ay2) and (ax2, ay2) in obstacles:
                adj_pen += 1

        tup = (my_best_gap, my_min_dist, adj_pen)
        # Include move for deterministic tie-break
        tup2 = (tup[0], tup[1], tup[2], dx, dy)
        if tup2 < (best[0], best[1], best[2], best_move[0], best_move[1]):
            best = (tup[0], tup[1], tup[2])
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]