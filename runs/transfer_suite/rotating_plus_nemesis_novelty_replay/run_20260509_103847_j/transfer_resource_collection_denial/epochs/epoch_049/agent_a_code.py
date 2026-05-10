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

    best = None  # (score, tie, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best resource we could be closer to than opponent after this move.
        best_margin = -10**9
        best_dist = 10**9
        closest_opp_block = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer
            if margin > best_margin or (margin == best_margin and (ds < best_dist or (ds == best_dist and man(nx, ny, ox, oy) < closest_opp_block))):
                best_margin = margin
                best_dist = ds
                closest_opp_block = man(nx, ny, ox, oy)

        # If we can contest, prioritize larger margin then smaller own distance.
        # Otherwise, head to a resource that is also closer to us than the opponent is (if any),
        # but otherwise just minimize our distance to the closest resource.
        if best_margin > 0:
            score = (2_000_000 * best_margin) - best_dist
            tie = (best_dist, man(nx, ny, ox, oy))
        else:
            # Find best "effort" move: minimize our distance to the nearest resource, but add small
            # preference for increasing distance from opponent (to reduce immediate denial).
            dmin = min(man(nx, ny, rx, ry) for rx, ry in resources)
            score = (-dmin) + (0.05 * man(nx, ny, ox, oy))
            tie = (dmin, man(nx, ny, ox, oy))

        key = (score, -tie[0], tie[1], dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]