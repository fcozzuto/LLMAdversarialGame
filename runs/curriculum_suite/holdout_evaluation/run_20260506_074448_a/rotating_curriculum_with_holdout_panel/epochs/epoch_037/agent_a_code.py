def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def center_bias(x, y):
        dx = x - cx
        dy = y - cy
        return -0.03 * (dx * dx + dy * dy)

    # If no resources, drift toward center while staying safe.
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = center_bias(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Consider candidate next squares; maximize contest advantage on resources.
    best_move = [0, 0]
    best_val = -10**18
    # Tie-break deterministically by preferring moves closer to opponent (more interception pressure)
    best_int = 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = man(nx, ny, ox, oy)
        # compute strongest advantage over all resources:
        # advantage > 0 means we're closer than opponent.
        best_adv = -10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_me
            if adv > best_adv:
                best_adv = adv

        # Additional small term: avoid moving away from the resource that we can beat soonest.
        # Approximate by pulling toward the best-beatable resource using its distance.
        pull = 0.0
        # find one resource achieving best_adv to pull toward it
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_opp - d_me == best_adv:
                pull = -0.02 * d_me
                break

        # Slight preference to reduce own distance to opponent when contesting (interceptor niche)
        # and to reduce edge-running.
        edge_pen = 0.0
        dist_to_edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        edge_pen = -0.01 * dist_to_edge

        val = 2.0 * best_adv + pull + center_bias(nx, ny) + (-0.03 * my_d) + edge_pen
        # If best_adv is negative for all resources, still try to maximize (least bad) best_adv.
        # Deterministic tie-break:
        inter = man(nx, ny, ox, oy)
        if val > best_val or (val == best_val and inter < best_int):
            best_val = val
            best_int = inter
            best_move = [dx, dy]

    return best_move