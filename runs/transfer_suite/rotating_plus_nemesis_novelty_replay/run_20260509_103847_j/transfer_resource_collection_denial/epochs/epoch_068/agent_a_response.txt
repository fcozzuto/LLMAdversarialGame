def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # Baseline: prefer resources where we can get there no later than opponent (or at least reduce their advantage).
    def target_value(x, y):
        best = None
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Higher is better:
            # 1) prioritize ds<=do (we contest/fetch first), using margin capped.
            # 2) among those, minimize ds.
            if ds <= do:
                v = (2_000_000 - (do - ds), -ds, rx, ry)
            else:
                # If we can't beat them, still pick where gap is smallest and ds is small.
                v = (-(do - ds), -ds, rx, ry)
            if best is None or v > best:
                best = v
        return best

    best_move = None  # (value_tuple, dx, dy)
    base = target_value(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v = target_value(nx, ny)
        # Also ensure we don't drift to a state worse for resource access than current target.
        # Tie-break deterministically by move ordering via v.
        if best_move is None or v > best_move[0] or (v == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (v, dx, dy)

    # If all adjacent valid moves were blocked, try to return a safe stay.
    if best_move is None:
        return [0, 0]

    return [best_move[1], best_move[2]]