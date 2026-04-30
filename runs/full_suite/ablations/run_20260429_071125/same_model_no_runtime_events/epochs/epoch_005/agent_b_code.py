def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)  # drift away deterministically
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose the resource with maximum distance advantage: (opponent - self)
    best_rx = best_ry = None
    best_adv = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv = adv
            best_ds = ds
            best_rx, best_ry = rx, ry

    # Move to best neighbor that improves outcome; include opponent pressure to avoid walking into races.
    rx, ry = best_rx, best_ry
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Primary: reduce my distance; Secondary: increase my advantage; Tertiary: break ties by smaller move (prefer straight-ish)
        v = (opd - myd) * 1000 - myd * 3
        if dx == 0 and dy == 0:
            v -= 50
        if abs(dx) + abs(dy) == 2:
            v -= 1
        if v > bestv:
            bestv = v
            best = (dx, dy)

    # If we can't improve (all look bad), switch to the globally best resource for next-step by local evaluation.
    if bestv < -10**8:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # Evaluate best resource from this next position
            local_best = -10**18
            for rx2, ry2 in resources:
                myd = cheb(nx, ny, rx2, ry2)
                opd = cheb(ox, oy, rx2, ry2)
                local_best = max(local_best, (opd - myd) * 1000 - myd)
            v = local_best
            if v > bestv:
                bestv = v
                best = (dx, dy)

    return [best[0], best[1]]