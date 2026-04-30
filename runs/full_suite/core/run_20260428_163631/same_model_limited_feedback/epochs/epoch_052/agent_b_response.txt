def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy) ** 0.5

    # Pick a target resource: prefer ones we're more likely to secure than opponent
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Deterministic tie-breaker by coordinates
        val = myd - 1.25 * (opd - myd)  # encourages going for resources opponent isn't closest to
        val += 0.001 * (rx * 8 + ry)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        # If no resources (unlikely), just drift away from opponent while staying valid
        tx, ty = sx, sy
    else:
        tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Strategy shift: if we are behind (opponent closer to target), prioritize intercepting their nearest resources
    # Approximate by using opponent distance to our chosen target; if they are much closer, aim for their "implied" target:
    if best is not None:
        myd0 = dist(sx, sy, tx, ty)
        opd0 = dist(ox, oy, tx, ty)
        if opd0 + 0.8 < myd0:
            # choose a new target: resource minimizing (opponent distance - my distance)
            best2 = None
            best2_val = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = dist(sx, sy, rx, ry)
                opd = dist(ox, oy, rx, ry)
                val = (opd - myd) + 0.001 * (rx * 8 + ry)
                if best2_val is None or val < best2_val:
                    best2_val = val
                    best2 = (rx, ry)
            if best2 is not None:
                tx, ty = best2

    # Evaluate candidate move
    best_move = (0, 0, None)
    for dx, dy, nx, ny in moves:
        myd = dist(nx, ny, tx, ty)
        opd = dist(nx, ny, ox, oy)
        # Secondary: avoid getting too close to opponent if it doesn't help resource acquisition
        # Deterministic tie-break by move order
        score = myd - 0.18 * opd + 0.0001 * ((dx + 1) * 3 + (dy + 1))
        if best_move[2] is None or score < best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]