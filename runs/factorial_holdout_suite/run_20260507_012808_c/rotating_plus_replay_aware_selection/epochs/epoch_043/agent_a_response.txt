def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [tuple(r) for r in resources]
    res_set = set(res)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = [0, 0]
    best_val = -10**18
    # Precompute opponent distances to each resource for deterministic comparisons
    oppd = {(rx, ry): man(ox, oy, rx, ry) for rx, ry in res}

    # Evaluate each possible next step by how much sooner we can reach a resource than the opponent
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pickup = 1 if (nx, ny) in res_set else 0
        my_best_gap = -10**9  # higher is better: opp_dist - my_dist
        my_closest = 10**9   # smaller is better
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            gap = oppd[(rx, ry)] - myd
            if gap > my_best_gap:
                my_best_gap = gap
            if myd < my_closest:
                my_closest = myd
        # Prefer (1) immediate pickup, (2) larger ability to arrive sooner than opponent,
        # (3) being closer overall, (4) keeping distance from opponent when gaps are similar.
        opp_dist_now = man(nx, ny, ox, oy)
        val = 5.0 * pickup + 1.2 * my_best_gap - 0.15 * my_closest + 0.02 * opp_dist_now
        if val > best_val or (val == best_val and (dx, dy) < tuple(best)):
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]