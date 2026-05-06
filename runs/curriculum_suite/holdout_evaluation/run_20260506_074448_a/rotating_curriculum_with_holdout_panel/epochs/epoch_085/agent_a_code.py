def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources") or []) if 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx = 1 if sx < cx else -1 if sx > cx else 0
        ty = 1 if sy < cy else -1 if sy > cy else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    def d2(ax, ay, bx, by):
        x = ax - bx
        y = ay - by
        return x * x + y * y

    # One-step lookahead, minimax-ish: prefer moves that make us closer to a resource
    # than the opponent is, while also improving our nearest resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Self improvement
        self_best = 10**18
        opp_best = 10**18
        gap_best = -10**18
        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od
            g = od - sd  # positive means we are closer (in squared distance)
            if g > gap_best: gap_best = g

        # Prefer winning contested targets (gap_best), otherwise still move toward nearest resource.
        val = 3.0 * gap_best - 0.3 * self_best + 0.05 * (opp_best - self_best)
        # Deterministic tie-break: lexicographically smallest (dx,dy)
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move