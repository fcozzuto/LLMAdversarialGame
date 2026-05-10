def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Phase select: prefer resources where we can be at least as close as opponent (contesting).
    best = None  # (priority, rx, ry)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # priority: lower is better; ensure deterministic selection
        if ds <= do:
            pri = (0, ds, -(do - ds), rx, ry)
        else:
            pri = (1, do - ds, ds, rx, ry)
        if best is None or pri < best[0]:
            best = (pri, rx, ry)

    tx, ty = best[1], best[2]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Move evaluation: minimize our distance, avoid getting worse relative to opponent, and avoid stepping near obstacles.
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)  # proxy for future contest: how close we are to opponent
        # also measure opponent distance to target (contest pressure)
        opp_dt = man(ox, oy, tx, ty)

        # obstacle proximity penalty
        near_obs = 0
        if obstacles:
            for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
                if (nx + ax, ny + ay) in obstacles:
                    near_obs += 1

        # want: smaller ds2, and not too far behind opponent on target
        rel = ds2 - opp_dt  # smaller is better
        # deterministic ordering: pack values
        key = (rel, ds2, do2, -near_obs, dx, dy)
        if key < best_move:
            best_move = key

    return [best_move[4], best_move[5]]