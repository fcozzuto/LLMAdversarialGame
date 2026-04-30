def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no info, stay.
    if not resources:
        return [0, 0]

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        # Score: try to secure a resource where we are relatively closer than opponent.
        cur_best = float("-inf")
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Big bonus if landing on resource.
            on_bonus = 50 if (nx == rx and ny == ry) else 0
            # Prefer targets we can reach sooner than opponent.
            rel = (do - ds)
            # Slight preference for nearer resources to avoid long detours.
            near_pref = -0.1 * ds
            cur_best = max(cur_best, on_bonus + rel + near_pref)

        # Defensive term: keep some distance from opponent to reduce contention fights.
        defend = -0.2 * man(nx, ny, ox, oy)
        val = cur_best + defend

        if val > best[0]:
            best = (val, dx, dy)
        elif val == best[0]:
            # Deterministic tie-breaker: prefer moves that reduce distance to best resource estimate.
            # (Use opponent-relative distance to the closest resource.)
            cur_closest = min((man(nx, ny, rx, ry) for rx, ry in resources))
            best_closest = min((man(sx + best[1], sy + best[2], rx, ry) for rx, ry in resources))
            if cur_closest < best_closest:
                best = (val, dx, dy)

    # If all candidate moves blocked, stay.
    if best[1] == 0 and best[2] == 0:
        return [0, 0]
    return [best[1], best[2]]