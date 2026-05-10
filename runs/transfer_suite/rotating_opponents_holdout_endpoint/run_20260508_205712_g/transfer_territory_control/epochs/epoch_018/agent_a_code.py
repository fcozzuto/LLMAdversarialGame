def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_val(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in oppT:
            return 2
        if (x, y) in unC:
            return 3
        if (x, y) in selfT:
            return 0
        return 0

    def nearest_dist_to_set(x, y, S):
        if not S:
            return 10**9
        md = 10**9
        for px, py in S:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    un_target = unC
    if not un_target:
        # No unclaimed: push into opponent territory
        un_target = oppT

    def score(nx, ny):
        sv = cell_val(nx, ny)
        if sv <= -10**8:
            return sv
        uc = 0
        opp_adj = 0
        for dx, dy in moves:
            ax, ay = nx + dx, ny + dy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in unC:
                uc += 1
            if (ax, ay) in oppT:
                opp_adj += 1
        dist = nearest_dist_to_set(nx, ny, un_target)
        # Prefer claiming fronts and cutting toward targets; stepping onto opponent is useful only near their frontier.
        return sv * 3 + uc * 1.4 + opp_adj * (2.0 if (nx, ny) in oppT else 1.0) - dist * 0.08

    best = None
    best_sc = -10**18
    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**9
        else:
            sc = score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]