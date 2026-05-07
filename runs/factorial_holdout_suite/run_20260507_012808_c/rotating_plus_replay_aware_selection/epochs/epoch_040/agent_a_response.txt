def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    def dist(x, y, p):
        return abs(p[0] - x) + abs(p[1] - y)

    # Choose a resource that we can reach relatively sooner than opponent
    opp_best = None
    opp_best_val = 10**18
    for r in res:
        my_d = dist(sx, sy, r)
        their_d = dist(ox, oy, r)
        val = (my_d - 0.75 * their_d)  # smaller is better for us
        if val < opp_best_val or (val == opp_best_val and (r[1], r[0]) < (opp_best[1], opp_best[0])):
            opp_best_val = val
            opp_best = r
    tx, ty = opp_best

    best = (10**18, 10**18, 0, 0)  # (score, dist_to_target, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = abs(tx - nx) + abs(ty - ny)
        pickup = 1 if (nx, ny) in res_set else 0

        # Approximate "denial": moving toward our target while (slightly) moving away from their current closest resource
        their_closest = 10**9
        for r in res:
            d = abs(r[0] - ox) + abs(r[1] - oy)
            if d < their_closest:
                their_closest = d
        their_pressure = their_closest - (abs(r[0] - nx) + abs(r[1] - ny) if False else their_closest)

        score = (0 if pickup else 1) * 1000000 + my_d - 0.05 * their_pressure
        if score < best[0] or (score == best[0] and my_d < best[1]) or (score == best[0] and my_d == best[1] and (dx, dy) < (best[2], best[3])):
            best = (score, my_d, dx, dy)

    dx, dy = best[2], best[3]
    nx, ny = sx + dx, sy + dy
    return [dx, dy] if valid(nx, ny) else [0, 0]