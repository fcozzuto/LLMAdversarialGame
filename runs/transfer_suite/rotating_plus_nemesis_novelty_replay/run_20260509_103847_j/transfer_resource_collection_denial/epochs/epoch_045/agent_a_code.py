def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_val = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate the best resource we could be aiming for from (nx, ny),
        # using opponent distance advantage and our absolute proximity.
        cur_best = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # Prefer targets where we are not worse than opponent (or at least reduce their advantage),
            # while breaking ties by our distance and preferring exact/near picks.
            # Larger is better: (do - ds), then closer ds.
            adv = do - ds
            pick = -ds
            key = (adv, pick, -min(ds, do))
            if cur_best is None or key > cur_best[0]:
                cur_best = (key, (rx, ry))

        if cur_best is None:
            continue

        # Global move score: maximize the local best target advantage; break ties deterministically.
        # Add slight bias toward reducing our distance to the single best resource by ds.
        (adv, pick, negmin) = cur_best[0]
        move_val = (adv, pick, negmin, -man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]