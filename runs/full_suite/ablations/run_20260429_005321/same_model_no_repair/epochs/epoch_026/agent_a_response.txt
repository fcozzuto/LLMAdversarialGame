def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose target resource where we are relatively closer than opponent (most positive advantage).
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer larger (do - ds), then smaller ds, then deterministic coordinates.
        key = (-(do - ds), ds, rx, ry)  # minimize
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Also consider taking/contest resources if current best is blocked nearby.
    def nearest_dist_from(x, y):
        # minimal Manhattan to any resource
        md = None
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    cur_self_d = man(sx, sy, tx, ty)
    cur_opp_d = man(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**7
        else:
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)  # opponent position unchanged this turn
            # Advantage: increase if we close toward target more than opponent is (in relative terms).
            advantage = (cur_opp_d - cur_self_d) - (opp_d - self_d)
            # Greedy toward target + slight preference for generally better resource proximity.
            val = (advantage * 120) + (cur_self_d - self_d) * 8
            nd = nearest_dist_from(nx, ny)
            val += (nearest_dist_from(sx, sy) - nd) * 3

            # Small bias to keep moving in direction that reduces distance to target.
            if self_d < cur_self_d:
                val += 1.5
            elif self_d == cur_self_d and (dx, dy) == (0, 0):
                val -= 0.2

            # Prefer avoiding squares that are adjacent to many obstacles (local safety).
            adj_obs = 0
            for adx, ady in deltas:
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_obs += 1
            val -= adj_obs * 0.5

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move