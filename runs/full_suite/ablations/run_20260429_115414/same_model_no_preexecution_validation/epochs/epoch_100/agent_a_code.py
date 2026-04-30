def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource_score(px, py):
        # Higher is better for us: we want smaller our distance and larger opponent distance.
        best = -10**18
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: win the race; Secondary: approach quickly; Tertiary: prefer nearer to our side.
            val = (opd - myd) * 200 - myd * 3 + abs((rx + ry) - (sx + sy)) * -1
            # Slight preference for resources closer to our current position to reduce dithering.
            val += -abs(myd - cheb(sx, sy, rx, ry))
            if val > best:
                best = val
        return best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # If opponent is very close to a resource, try to steal the race by prioritizing resources with worst opponent distance.
    # Otherwise, just do local greedy best_resource_score from each candidate.
    opp_threat = -10**18
    for rx, ry in resources:
        opp_threat = max(opp_threat, -cheb(ox, oy, rx, ry))
    threat_mode = opp_threat >= -2  # opponent is within ~2 (cheb) of some resource

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        v = best_resource_score(nx, ny)
        if threat_mode:
            # In threat mode, also slightly penalize moves that increase our distance to the currently best "race winner" target.
            # Choose that target by evaluating from current position.
            cur_best_target = None
            cur_best = -10**18
            for rx, ry in resources:
                myd = cheb(sx, sy, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                val = (opd - myd) * 200 - myd * 3
                if val > cur_best:
                    cur_best = val
                    cur_best_target = (rx, ry)
            if cur_best_target is not None:
                rx, ry = cur_best_target
                v -= cheb(nx, ny, rx, ry) * 2
        # Deterministic tie-breaker: prefer staying still then lower dx then lower dy
        v += (0 if (dx == 0 and dy == 0) else -0.0001)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]