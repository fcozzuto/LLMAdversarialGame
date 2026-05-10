def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = None

    # Evaluate each possible move by greedy target selection with opponent race + obstacle penalty
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
            dx, dy = 0, 0
        blocked = (nx, ny) in obstacles
        myd_mult = 1
        myd_base_pen = 0
        if blocked:
            myd_base_pen = 1000

        # Find best target for this move (deterministic scan order)
        local_best = None
        for rx, ry in resources:
            # Race advantage: positive means opponent farther (good for us)
            myd = cd(nx, ny, rx, ry)
            opd = cd(ox, oy, rx, ry)
            adv = opd - myd  # higher is better
            # Small tie-break toward nearer and toward center
            dist_tieb = -myd
            center = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
            # Strongly avoid targets where opponent is already closer (unless we are much closer after move)
            race_pen = 0
            if adv < 0:
                race_pen = (-adv) * 3
            # Mild preference for collecting something quickly over late max advantage
            time_bias = -myd_mult * myd
            key = (adv >= 0, adv, time_bias, dist_tieb, center, -(rx + 7 * ry))
            val = myd_base_pen + race_pen
            # Convert key to a comparable score deterministically
            # Since Python compares tuples lexicographically, reuse key ordering by mapping to scalar-ish:
            cand = (key, -(myd) - 0.01 * opd)
            if local_best is None or cand > local_best:
                local_best = cand

        # local_best[0] drives; extract a deterministic scalar proxy from tuple components
        # Use lexicographic components again to compare moves without non-deterministic float ops.
        # Recompute a comparable score from the first element of local_best.
        if local_best is None:
            score = (-10**9, 0)
        else:
            key = local_best[0]
            # key is (adv>=0, adv, time_bias, dist_tieb, center, -sum)
            score = key
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]