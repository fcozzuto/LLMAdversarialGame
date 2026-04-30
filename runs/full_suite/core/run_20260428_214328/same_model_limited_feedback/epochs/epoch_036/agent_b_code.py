def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    obst = obstacles

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    # Choose resource to maximize our advantage (opponent slower than us).
    best = None
    best_val = -1e18
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we're closer to; break ties by farther from opponent (harder to steal).
        val = (do - ds) * 10.0 - ds * 0.1
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        tx, ty = (ox, oy)
    else:
        tx, ty = best

    # If opponent is on/near our target, pivot to a runner-up to deny.
    if best is not None and dist((ox, oy), (tx, ty)) <= 1.5:
        alt = None
        alt_val = -1e18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            val = (do - ds) * 10.0 - ds * 0.05
            if (rx, ry) != (tx, ty) and val > alt_val:
                alt_val = val
                alt = (rx, ry)
        if alt is not None:
            tx, ty = alt

    # Move one step towards target while avoiding obstacles (or staying if blocked).
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestd = 1e18
    tie = 1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        d = dist((nx, ny), (tx, ty))
        # Slight preference for moves that also increase our distance from opponent (defensive denial).
        oppd = dist((nx, ny), (ox, oy))
        score = d - oppd * 0.02
        if score < bestd - 1e-9:
            bestd = score
            bestm = (dx, dy)
            tie = d
        elif abs(score - bestd) <= 1e-9 and d < tie:
            bestm = (dx, dy)
            tie = d

    return [int(bestm[0]), int(bestm[1])]