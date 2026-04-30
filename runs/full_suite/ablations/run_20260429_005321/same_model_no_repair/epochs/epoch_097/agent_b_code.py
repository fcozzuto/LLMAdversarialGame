def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]

    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def local_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obst:
                p += 2
        if (x, y) in obst:
            p += 10**6
        return p

    # If no resources, just run away.
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy) - local_pen(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Score each candidate move by best resource we can secure (or deny).
    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym, nx, ny in legal:
        # Find resources where we are closer than opponent (or at least not behind).
        best_target_val = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer winning/contesting near-term; penalize giving opponent a fast grab.
            # Also slightly prefer nearer resources regardless of contest.
            contest = (d_opp - d_self)
            if contest >= 0:
                v = 1000 * contest - 10 * d_self
            else:
                v = -1200 * (-contest) - 10 * d_self
            # Additional tie-breakers: avoid targets too "dangerously" surrounded.
            v -= local_pen(rx, ry)
            if v > best_target_val:
                best_target_val = v

        # Tactical layer: keep distance from opponent if we can't secure a target.
        opp_dist = cheb(nx, ny, ox, oy)
        # If best_target_val is very negative, emphasize running away.
        run_weight = 1.0
        if best_target_val < -500:
            run_weight = 4.0
        val = best_target_val + run_weight * opp_dist - local_pen(nx, ny)

        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]