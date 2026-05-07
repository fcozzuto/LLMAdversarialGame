def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            if (p[0], p[1]) not in obs:
                res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            dirs.append((dx, dy))

    def opp_best_after_step(target):
        d0 = md((ox, oy), target)
        # greedy opponent can reduce by at most 1 per turn (ignoring obstacles)
        return max(0, d0 - 1)

    best_move = (0, 0)
    best_score = -10**18

    if (sx, sy) in res:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        my_after = (nx, ny)
        # Choose target that maximizes our lead over opponent's ability
        # plus a small preference for immediate closeness.
        local_best = -10**18
        for r in res:
            d_my = md(my_after, r)
            d_opp = opp_best_after_step(r)
            lead = d_opp - d_my  # positive means we are closer
            val = 10 * lead - d_my
            if val > local_best:
                local_best = val

        # tie-breaker: prefer moves that get us closer to the overall nearest resource
        nearest = min(res, key=lambda t: md(my_after, t))
        d_near = md(my_after, nearest)
        score = local_best - 0.1 * d_near

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]