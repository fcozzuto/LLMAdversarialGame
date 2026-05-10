def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    rem = observation.get("remaining_resource_count", len(resources))
    scarcity = 1 if rem <= 4 else 0
    opp_pressure = 1 if man(sx, sy, ox, oy) <= 3 else 0

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Precompute resource ordering by our distance
    res_sorted = sorted(resources, key=lambda p: man(sx, sy, p[0], p[1]))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy, nx, ny in candidates:
        score = 0.0
        # Immediate capture
        for rx, ry in resources:
            if nx == rx and ny == ry:
                score += 1e6 + 1e3 * scarcity
        # Race / denial evaluation on top few targets
        for i, (rx, ry) in enumerate(res_sorted[:6]):
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer moving closer to a resource where we can stay ahead
            if ds < do:
                ahead = do - ds
                score += (100.0 / (1 + ds)) * (1 + 0.2 * i)
                score += 20.0 * ahead
                if scarcity:
                    score += 10.0 * (ahead >= 1)
            elif ds == do:
                score += 2.0 * (100.0 / (1 + ds))
            else:
                # Avoid enabling opponent capture too easily
                score -= (30.0 / (1 + ds)) * (1 + 0.25 * i)
                score -= 10.0 * (do - ds)

        # Block line-of-approach near nearest resource if opponent is close
        if opp_pressure:
            nearest = res_sorted[0]
            rrx, rry = nearest
            if man(nx, ny, rrx, rry) <= 1 and man(ox, oy, rrx, rry) <= 2:
                score += 80.0

        # Obstacle proximity: slight penalty to prevent accidental traps
        if obstacles:
            min_ob = min((man(nx, ny, bx, by) for bx, by in obstacles), default=10)
            score -= 3.0 / (1 + min_ob)

        # Small preference toward not increasing distance to best target
        rrx, rry = res_sorted[0]
        score += 1.5 * (man(sx, sy, rrx, rry) - man(nx, ny, rrx, rry))

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]