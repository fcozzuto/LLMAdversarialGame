def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    selfT = set(tuple(p) for p in observation.get("self_territory", []))
    oppT = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def score_cell(nx, ny):
        nxt = (nx, ny)
        s = 0.0
        if nxt in oppT:
            s += 6.0 - 0.01 * man(nx, ny, ox, oy)
        elif nxt in unclaimed:
            s += 3.5

        # Frontier pressure: prefer cells adjacent to opp territory or unclaimed clusters
        adj_opp = 0
        adj_un = 0
        adj_free = 0
        for dx, dy in neigh:
            ax, ay = nx + dx, ny + dy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in oppT:
                adj_opp += 1
            if (ax, ay) in unclaimed:
                adj_un += 1
            if (ax, ay) not in selfT and (ax, ay) not in oppT:
                adj_free += 1
        s += 0.35 * adj_opp
        s += 0.20 * adj_un

        # Avoid getting pulled into the opponent: if we step onto/near their cells, ensure we don't do
        # a big dive unless it increases adjacency.
        d_now = man(sx, sy, ox, oy)
        d_new = man(nx, ny, ox, oy)
        if d_new < d_now and nxt not in oppT:
            s -= 0.15 * (d_now - d_new)
        if nxt in selfT:
            s -= 0.2  # don't waste time unless no better move exists
        if (nx, ny) in unclaimed:
            s -= 0.01 * (d_new)  # slight preference for closer unclaimed

        return s

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)

        # Secondary keys: approach nearest opponent "frontier" and nearest unclaimed
        if unclaimed:
            dist_un = min(m + n for m, n in [min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed), 0])  # trick to keep deterministic
            dist_un = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
        else:
            dist_un = 10**9

        # Prefer moves that reduce distance to closest opp cell (edge-claim counter)
        dist_opp = min((abs(nx - tx) + abs(ny - ty) for (tx, ty) in oppT), default=10**9)

        # Lexicographic: higher score, then closer to opp, then closer to unclaimed, then stable (prefer diagonal-less)
        key = (sc, -dist_opp, -dist_un, - (dx != 0 and dy != 0))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]