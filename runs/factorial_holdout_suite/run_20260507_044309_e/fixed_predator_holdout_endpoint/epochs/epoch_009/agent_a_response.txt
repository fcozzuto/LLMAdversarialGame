def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev (diagonal) distance

    cand = []
    for dx0 in (-1, 0, 1):
        for dy0 in (-1, 0, 1):
            nx, ny = sx + dx0, sy + dy0
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx0, dy0, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        mx = (sx + ox) // 2
        my = (sy + oy) // 2
        best = None
        bestv = None
        for dx0, dy0, nx, ny in cand:
            v = -((nx - mx) * (nx - mx) + (ny - my) * (ny - my)) - 0.1 * (abs(nx - ox) + abs(ny - oy))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx0, dy0)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Race for resources: prefer those where we can arrive not much later than opponent.
    best_move = None
    best_val = None
    for dx0, dy0, nx, ny in cand:
        # Small bias toward staying flexible near the center of remaining resources
        best_local = -10**18
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # Positive if we are closer (or can arrive at least as soon with diagonals)
            lead = opp_d - self_d
            v = 10.0 * lead - 0.5 * self_d
            # If opponent is much closer, down-rank but don't ignore (could be blocked/deny elsewhere)
            v -= 0.8 * max(0, -lead)
            if v > best_local:
                best_local = v
        # Add tie-breaker: avoid moves that increase distance to the "best" target too much
        # using current-cell total advantage proxy
        total_adv = 0
        for rx, ry in resources:
            self_d_now = dist(nx, ny, rx, ry)
            opp_d_now = dist(ox, oy, rx, ry)
            total_adv += (opp_d_now - self_d_now)
            break
        # Keep opponent-awareness: prevent stepping into worse positions when we are far behind
        opp_prox = dist(nx, ny, ox, oy)
        v2 = best_local + 0.01 * total_adv - 0.02 * opp_prox
        if best_val is None or v2 > best_val:
            best_val = v2
            best_move = (dx0, dy0)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]