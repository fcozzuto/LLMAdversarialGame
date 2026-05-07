def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx + dy
    res_set = {(r[0], r[1]) for r in resources}
    if not res_set:
        return [0, 0]

    best = [0, 0]
    best_val = -10**18
    best_tie = (10**9, 10**9)

    # Evaluate by: landing on resource, then maximizing (opponent_advantage) i.e. we prefer targets we reach sooner
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in res_set:
            # Highest priority: immediate collection
            return [dx, dy]

        self_best = 10**9
        opp_best = 10**9
        for rx, ry in res_set:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od

        # Prefer moves that reduce our distance more than opponent's; also keep some mobility
        # Score: (opp_dist - self_dist) is larger when we are closer than opponent
        val = (opp_best - self_best) * 1000 - self_best
        # Tie-break deterministically: prefer lower self_best, then prefer moves toward increasing x then y (fixed ordering)
        tie = (self_best, - (dx * 2 + dy))  # deterministic
        if val > best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best = [dx, dy]

    return best