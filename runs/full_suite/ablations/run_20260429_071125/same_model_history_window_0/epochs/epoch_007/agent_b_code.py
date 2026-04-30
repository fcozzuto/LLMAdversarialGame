def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    # If no resources, try to drift away from opponent while staying safe.
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            val = dist((nx, ny), (ox, oy))  # maximize distance
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Materially different: prioritize resources that are far from opponent (less contest),
    # then move greedily toward them while avoiding opponent chasing.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue

        my_d_opp = dist((nx, ny), (ox, oy))
        # Prefer to keep or increase distance vs opponent.
        opp_d_now = dist((sx, sy), (ox, oy))
        keep = my_d_opp - opp_d_now  # >0 means moving away

        # For this move, choose the best target resource.
        best_target_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_to = dist((nx, ny), (rx, ry))
            opp_to = dist((ox, oy), (rx, ry))
            # Larger opp_to means harder for opponent to get (contest reduction).
            # Also keep going to closer resources.
            v = (-my_to) + (2 * opp_to) + (keep * 3)
            # If resource is exactly where we'd be, make it very attractive.
            if nx == rx and ny == ry:
                v += 10**6
            if v > best_target_val:
                best_target_val = v

        # Small tie-breaker: prefer staying within bounds and not oscillating toward opponent.
        val = best_target_val + my_d_opp // 10
        if val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]