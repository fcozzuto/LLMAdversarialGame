def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x0, y0 = observation["self_position"]
    xo, yo = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    best_t = None
    best_score = -10**18

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    # Pick a target resource: prefer nearer than opponent, but still reachable.
    for r in resources:
        if tuple(r) in obstacles:
            continue
        myd = dist2((x0, y0), r)
        opd = dist2((xo, yo), r)
        # If myd much smaller, strongly prefer; if I'm behind, still possible.
        # Also prefer resources that are not extremely far.
        score = (opd - myd) * 10 - myd - abs(opd - myd) * 0.1
        # Deterministic tie-breaker: lexicographic
        if best_t is None or score > best_score or (score == best_score and (r[0], r[1]) < (best_t[0], best_t[1])):
            best_score = score
            best_t = r

    # If no resources (shouldn't happen), fall back to staying or moving away from opponent.
    if best_t is None:
        cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        best = (0, 0)
        bestd = -10**18
        for dx, dy in cand:
            x = x0 + dx
            y = y0 + dy
            if x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles:
                continue
            d = dist2((x, y), (xo, yo))
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    tx, ty = best_t
    directions = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**18

    myd0 = dist2((x0, y0), (tx, ty))
    opd0 = dist2((xo, yo), (tx, ty))
    for dx, dy in directions:
        x = x0 + dx
        y = y0 + dy
        if x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles:
            continue
        myd1 = dist2((x, y), (tx, ty))
        # Try to improve relative position vs opponent on the target.
        opd1 = dist2((xo, yo), (tx, ty))  # opponent position unchanged this step
        rel = opd1 - myd1
        # Also add slight penalty for moving closer to opponent to reduce chance of giving them better trades.
        d_to_opp = dist2((x, y), (xo, yo))
        val = rel * 20 - myd1 - (myd1 - myd0 == 0) * 3 + d_to_opp * 0.02
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]