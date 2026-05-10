def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):  # Chebyshev (diagonal-friendly)
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources that we can reach sooner than opponent from the next state.
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # If stepping into obstacle is rejected by engine anyway, this keeps us safer deterministically.
        myd_opp = 0
        worst = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Main objective: minimize our "lead cost"; add small term to break ties by closer-to-us.
            score = myd - 0.85 * (opd - myd)  # strongly favors gaining/keeping a lead
            score += 0.02 * (myd + abs(rx - ox) * 0)  # deterministic tie nudging
            if worst is None or score < worst:
                worst = score
        # Also encourage progressing away from opponent's likely sweep line: maximize increase in x-y alignment distance.
        align = abs((nx - ox)) + abs((ny - oy))
        score2 = worst - 0.03 * align
        if best is None or score2 < best or (score2 == best and (dx, dy) < (best_move[0], best_move[1])):
            best = score2
            best_move = [dx, dy]

    return best_move