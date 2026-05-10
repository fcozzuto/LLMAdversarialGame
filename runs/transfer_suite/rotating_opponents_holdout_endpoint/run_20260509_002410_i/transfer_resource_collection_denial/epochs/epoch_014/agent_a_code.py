def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def adj_obs_pen(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacle_set:
                    p += 1
        return p

    if not resources:
        return [0, 0]

    # Moves: deterministic order favors forward-ish then diagonals.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_step_to_res = 0
        opp_step_to_res = 0
        # Evaluate contest advantage for the most winnable resource.
        # score higher if we are closer than opponent; also prefer immediate collection.
        local_best = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Big bump if stepping onto a resource.
            bump = 20 if myd == 0 else 0
            # Prefer resources we can secure earlier.
            val = (opd - myd) + bump - 0.15 * (abs(rx - ox) + abs(ry - oy)) - 0.05 * (adj_obs_pen(nx, ny))
            if val > local_best:
                local_best = val
                my_step_to_res = myd
                opp_step_to_res = opd

        # Secondary tie-break: maximize resource density closeness and minimize exposure to obstacles.
        # (Deterministic, small magnitudes.)
        density = 0
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d <= 2:
                density += (3 - d)
        val2 = local_best + 0.05 * density - 0.1 * adj_obs_pen(nx, ny) - 0.01 * (my_step_to_res)

        if best is None or val2 > best_val:
            best_val = val2
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]