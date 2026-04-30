def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation["resources"]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_val = -10**9
    # Target resource that gives the best advantage (prefer being closer than opponent)
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs_set:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        val = (do - ds) * 10 - ds  # strong anti-collision priority
        # If tie, prefer nearer to prevent wandering
        if val > best_val:
            best_val = val
            best = (rx, ry)
    if best is None:
        best = (w // 2, h // 2)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose a move that reduces distance to target while avoiding obstacles
    cur_d = dist((sx, sy), (tx, ty))
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer getting closer; also slightly prefer squares where opponent isn't simultaneously advantaged
        do = dist((ox, oy), (tx, ty))
        score = (cur_d - nd) * 100 - nd - (do - nd)  # deterministic tie-break
        candidates.append((score, dx, dy))
    # If all moves blocked or off-grid, allow staying
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]

    # If opponent is at nearly the same distance, shift to a small defensive sidestep toward obstacles-adjacent paths
    if resources:
        min_ds_self = 10**9
        min_ds_opp = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in obs_set:
                continue
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            if d1 < min_ds_self:
                min_ds_self = d1
            if d2 < min_ds_opp:
                min_ds_opp = d2
        if abs(min_ds_self - min_ds_opp) <= 1:
            # pick move that maximizes distance from opponent (simple juke)
            best_flee = (-10**9, dx, dy)
            for dx2, dy2 in deltas:
                nx, ny = sx + dx2, sy + dy2
                if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                    continue
                opp_d = dist((nx, ny), (ox, oy))
                if (opp_d, -abs(dx2), -abs(dy2)) > (best_flee[0], 0, 0):
                    best_flee = (opp_d, dx2, dy2)
            dx, dy = best_flee[1], best_flee[2]

    return [int(dx), int(dy)]