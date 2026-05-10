def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Candidate deltas (deterministic order)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If unclaimed exists, aim to expand toward nearest frontier (opponent border weighted)
    if unclaimed:
        targets = list(unclaimed)
        # small bias to targets near opponent territory to counter territory_counterclaim
        def near_opp_pen(cell):
            cx, cy = cell
            for ax, ay in opp_t:
                if abs(ax - cx) <= 1 and abs(ay - cy) <= 1:
                    return 0
            return 1
    else:
        targets = list(opp_t)
        def near_opp_pen(cell): return 0

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # find nearest target for guidance
    if targets:
        best_target = min(targets, key=lambda c: (dist((sx, sy), c), near_opp_pen(c), c[0], c[1]))
    else:
        best_target = (sx, sy)

    # Evaluate one-step move by local expected gains
    def cell_score(nx, ny):
        if (nx, ny) in obstacles:  # illegal -> should not happen, but keep safe
            return -10**9
        base = 0
        if (nx, ny) in opp_t:
            base += 8  # flip pressure
        elif (nx, ny) in unclaimed:
            base += 5  # secure territory
        elif (nx, ny) in self_t:
            base += 1  # maintain control
        else:
            base += 0  # entering neither: likely edge/undefined; keep neutral

        # Encourage moving toward target
        base += -0.5 * dist((nx, ny), best_target)

        # Prefer moves that create adjacency to unclaimed/opponent front (future expansion)
        adj = 0
        for dx, dy in dirs8:
            ax, ay = nx + dx, ny + dy
            if inb(ax, ay) and (ax, ay) not in obstacles and (ax, ay) != (sx, sy):
                if (ax, ay) in unclaimed:
                    adj += 2
                elif (ax, ay) in opp_t:
                    adj += 1
        base += adj

        # Slight penalty for moving directly into opponent-influence (cells adjacent to many opp cells)
        infl = 0
        for ax, ay in opp_t:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                infl += 1
        base += -0.1 * infl
        return base

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = cell_score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]