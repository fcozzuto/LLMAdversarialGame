def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}
    res = [(p[0], p[1]) for p in resources]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        # Base: move toward best resource (closest by Chebyshev from next pos)
        best_r = None
        best_m = 10**9
        best_key = (10**9, 10**9, 10**9)
        for rx, ry in res:
            m = cheb(nx, ny, rx, ry)
            key = (m, ry, rx)
            if key < best_key:
                best_key = key
                best_m = m
                best_r = (rx, ry)

        if best_r is None:
            return 0

        rx, ry = best_r
        my_d = best_m
        # Opponent: avoid giving opponent a faster path to the same resource
        opp_d = cheb(ox, oy, rx, ry)
        opp_after = cheb(ox, oy, rx, ry)
        # If we're about to collect (adjacent or same step), prioritize heavily
        collect_bonus = 0
        if my_d == 0:
            collect_bonus = 1000
        elif my_d == 1:
            collect_bonus = 250

        # Slightly penalize moving near obstacles (local check)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj_pen += 3

        # Main objective: reduce my distance to target and don't let opponent be much closer
        # Use difference relative to opponent current distance (deterministic, no opponent move modeling)
        adv = (opp_after - my_d)
        return (adv * 20) - (my_d * 5) + collect_bonus - adj_pen

    # If resources exist, choose the deterministic best move; else drift toward center of remaining resources area
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        val = score_move(nx, ny)
        # Tie-break deterministically: lexicographic (dy, dx) with prefer staying if equal
        tie = (val, -abs(dx), -abs(dy), -1 if (dx == 0 and dy == 0) else 0)
        # Convert to single comparable by using val then tie tuple ordering
        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)

    if best[0] == -10**18:
        # Fallback: any valid move deterministically preferring non-diagonal toward center-like
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[1], best[2]]