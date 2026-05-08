def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    turns = int(observation.get("turn_index", 0))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    behind = (observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_adj_opp(nx, ny):
        m = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in opp_t:
                    m += 1
        return m

    def score_cell(nx, ny):
        if (nx, ny) in self_t:
            base = 0.0
        elif (nx, ny) in opp_t:
            base = 7.0 if behind else 9.0
        elif (nx, ny) in unclaimed:
            base = 2.8 if not behind else 3.4
        else:
            base = 0.7

        dist_edge = abs(nx - cx) + abs(ny - cy)
        edge_pref = 0.25 if behind else 0.35  # when behind, take safe edge expansion; otherwise more aggressive edge growth
        s = base + edge_pref * dist_edge

        # Avoid walking into dense obstacle-adjacency traps
        obs_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    obs_adj += 1
        s -= 0.35 * obs_adj

        # If behind, prefer moves adjacent to opponent territory for faster flips
        s += (0.9 if behind else 0.35) * best_adj_opp(nx, ny)

        # Every 10 turns, a sole leader gets +0.5; if we're likely behind leader advantage, try to break.
        if turns % 10 == 9 and behind:
            if (nx, ny) in opp_t:
                s += 2.0
        return s

    best = None
    best_s = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        s = score_cell(nx, ny)
        # Deterministic tie-break: prefer larger dx then dy then staying (0,0) last
        tb = (dx, dy)
        if s > best_s or (s == best_s and (best is None or tb > (best[0], best[1]))):
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]