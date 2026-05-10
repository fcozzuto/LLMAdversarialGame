def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    oxp, oyp = opp_pos[0], opp_pos[1]

    obs = set((p[0], p[1]) for p in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    def score_cell(nx, ny):
        if (nx, ny) in obs:
            return -10**12
        # Base: prefer unclaimed (new territory), tolerate opponent (can flip), avoid going deep into opponent.
        base = 0.0
        if (nx, ny) in unclaimed:
            base += 5.0
        if (nx, ny) in opp:
            base += 1.0
        if (nx, ny) in selft:
            base += 2.0

        # Frontier pressure: count adjacent unclaimed cells
        frontier = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in unclaimed:
                    frontier += 1

        # Safety: stay away from opponent position (territory sweeper tends to cut)
        man_to_opp = abs(nx - oxp) + abs(ny - oyp)
        safety = 0.2 * man_to_opp

        # Tactical: if entering opponent, prefer edges near our territory
        adj_self = 0
        adj_opp = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay):
                    if (ax, ay) in selft:
                        adj_self += 1
                    if (ax, ay) in opp:
                        adj_opp += 1

        tactical = 0.0
        if (nx, ny) in opp:
            tactical += 0.8 * adj_self
            tactical -= 0.2 * adj_opp
            tactical += 0.05 * frontier
        else:
            tactical += 0.3 * adj_self
            tactical += 0.6 * frontier

        return base + 0.9 * frontier + safety + tactical

    # Deterministic tie-break: lexicographically smallest move among those with max score
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = score_cell(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]