def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Deterministic escape/advance: bias away from opponent, but vary by turn parity.
        tx, ty = (w - 1, h - 1) if (observation["turn_index"] % 2 == 0) else (0, h - 1)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_to_opp = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tx, ty)
            v = d_to_opp * 1000 + d_corner * 2 - (abs(nx - x) + abs(ny - y)) * 0.01
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Move evaluation: maximize ability to win/deny resources.
    best = (0, 0)
    bestv = -10**18
    parity = observation["turn_index"] & 1
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        score = 0
        # Base pressure: closer to resources than opponent.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                score += 200000
            # If we can reach strictly sooner (tie-breaking by parity), big reward; else mild penalty.
            if myd < opd:
                score += (opd - myd) * 4000 + 50
            elif myd == opd:
                score += (50 if ((rx + ry + parity) & 1) else -10)
            else:
                score -= (myd - opd) * 250
            # Slight preference to reduce opponent's closeness to the best target.
        # Also add preference to move toward the "frontier" resource where we currently lag least.
        # (This helps when denial isn't possible yet.)
        lag_best = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lag_best = min(lag_best, (myd - opd))
        score += (-lag_best) * 20
        # Avoid stepping into obstacle-adjacent dead zones by lightly penalizing low-mobility.
        mob = 0
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if valid(nnx, nny):
                mob += 1
        score += mob * 3
        if score > bestv:
            bestv = score
            best = (dx, dy)
        elif score == bestv:
            # Deterministic tie-break: prefer moves that decrease distance to opponent (denial pressure)
            if cheb(nx, ny, ox, oy) < cheb(x + best[0], y + best[1], ox, oy):
                best = (dx, dy)

    return [best[0], best[1]]