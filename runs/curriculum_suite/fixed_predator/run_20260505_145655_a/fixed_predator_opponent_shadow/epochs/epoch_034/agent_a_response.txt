def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Move evaluation: take resources we can reach sooner than opponent; also reduce opponent progress.
    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y  # deterministic fallback; engine would keep us anyway

        sc = 0.0
        for rx, ry in resources:
            dm = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)

            # Favor states where we are ahead on valuable nearby resources.
            # Stronger weight for closer resources to create decisive motion.
            ahead = do - dm  # positive if we are closer
            sc += (ahead * 12.0) - (dm * 1.2) + (do * 0.2)

        # Interception pressure: move to reduce distance to the resource currently closest to opponent.
        opp_target = min(resources, key=lambda r: man(r, (ox, oy)))
        dt_me = abs(opp_target[0] - nx) + abs(opp_target[1] - ny)
        dt_opp = abs(opp_target[0] - ox) + abs(opp_target[1] - oy)
        sc += (dt_opp - dt_me) * 6.0

        # Slightly prefer moves that improve our overall closeness to the set of resources.
        near_me = min(resources, key=lambda r: man(r, (nx, ny)))
        sc += (25.0 / (1.0 + man(near_me, (nx, ny)))) - (25.0 / (1.0 + man(near_me, (ox, oy))))

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]