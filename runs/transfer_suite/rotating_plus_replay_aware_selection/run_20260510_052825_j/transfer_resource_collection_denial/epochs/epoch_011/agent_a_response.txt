def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    best = None
    best_score = None

    # Pre-filter resources that are on obstacles (shouldn't happen, but be safe)
    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles]
    if not res:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Choose target resource that we are relatively closer to than opponent.
        # Score = advantage (opp-self) - small penalty for our distance.
        local_best = None
        local_target_d = None
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            # Encourage shorter paths among equal advantage; also avoid walking into very long detours
            val = adv * 1000 - sd
            if local_best is None or val > local_best:
                local_best = val
                local_target_d = sd

        # Secondary: slightly prefer staying mobile (don’t over-commit to far targets)
        # and prefer moves that reduce our distance to that best target.
        if best_score is None or local_best > best_score:
            best_score = local_best
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best