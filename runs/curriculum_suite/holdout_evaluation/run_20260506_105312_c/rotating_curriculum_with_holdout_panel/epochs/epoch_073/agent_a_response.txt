def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Choose a target resource we can reach not later than opponent; else fall back to closest to us.
    best_target = None
    best_td = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not in_bounds(rx, ry) or (rx, ry) in obs:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        td = (0 if ds <= do else 1, ds - do, ds, rx, ry)
        if best_target is None or td < best_td:
            best_target = (rx, ry)
            best_td = td

    tx, ty = best_target if best_target is not None else (int(resources[0][0]), int(resources[0][1]))

    # Score moves: prioritize progress to target; if ties, prefer moves that worsen opponent access to the target.
    # Also add a small bias for moving toward any resource we can reach.
    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            return (10**9,)
        ds_t = abs(tx - nx) + abs(ty - ny)
        do_t = abs(tx - ox) + abs(ty - oy)
        # "Cut" effect: reduce our distance while trying to keep opponent far from the target.
        # Opponent cannot move in this scoring step, but this correlates with access over time.
        cut = (do_t - ds_t)
        # Secondary: encourage heading toward a resource we can beat opponent on.
        best_gap = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not in_bounds(rx, ry) or (rx, ry) in obs:
                continue
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            best_gap = max(best_gap, ds <= do and (do - ds) or -(ds - do))
        return (ds_t, -cut, -best_gap, dx, dy)

    best = None
    best_key = None
    for dx, dy in moves:
        key = move_score(dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]