def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # If no resources, drift toward center while keeping away from obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    # One-step lookahead: choose move that improves our race lead, with extra contention for opponent's current row.
    alpha = 0.18  # contest opponent row (sweep_rows archetype)
    beta = 0.9    # favor states where opponent is farther to the best contested resource
    gamma = 0.08  # slight preference for moving closer to some resource

    opp_best = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if opp_best is None or d < opp_best:
            opp_best = d
    if opp_best is None:
        opp_best = 0

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Our best resource after this move, but favor those on/near opponent's row for contention.
        my_best = None
        contested_term = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            row_cont = abs(ry - oy)
            val = myd + alpha * row_cont - beta * oppd
            if my_best is None or val < my_best:
                my_best = val
                contested_term = row_cont

        # Add a small nudge toward reducing distance to overall nearest resource.
        nearest = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if nearest is None or d < nearest:
                nearest = d
        total = my_best + gamma * nearest + 0.01 * contested_term

        if best_val is None or total < best_val or (total == best_val and (dx, dy) < tuple(best_move)):
            best_val = total
            best_move = [dx, dy]

    return best_move if best_move != [0, 0] or ([sx, sy] not in obstacles) else [0, 0]