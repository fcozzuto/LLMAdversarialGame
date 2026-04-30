def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(int(p[0]), int(p[1])) for p in resources if len(p) >= 2]
    obs = set((int(p[0]), int(p[1])) for p in obstacles if len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy

    def min_obs_dist(x, y):
        if not obs:
            return 9
        d = 10**9
        for ax, ay in obs:
            dd = abs(x - ax) + abs(y - ay)
            if dd < d:
                d = dd
        return d

    if not res:
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = -man((nx, ny), (ox, oy)) - 2 * min_obs_dist(nx, ny)
            if score > best[0]:
                best = (score, dx, dy)
        if best[1] or best[2]:
            return [best[1], best[2]]
        return [0, 0]

    self_a = (sx, sy)
    opp_a = (ox, oy)

    best_r = res[0]
    best_k = -10**18
    for r in res:
        dself = cheb(self_a, r)
        dopp = cheb(opp_a, r)
        # Prefer targets where we are closer than opponent; break ties by being closer to target and farther from opponent.
        k = (dopp - dself) * 20 - dself * 3 + (opponent_bias := (dopp - dopp))  # deterministic no-op
        if k > best_k:
            best_k = k
            best_r = r

    tx, ty = best_r
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds = cheb((nx, ny), (tx, ty))
        do = cheb(opp_a, (tx, ty))
        # Gain if we reduce opponent's advantage; avoid obstacles.
        score = (do - ds) * 12 - ds * 3 - 2 * min_obs_dist(nx, ny)
        # Small tie-break: prefer moves closer to opponent when we can't secure target.
        score += -cheb((nx, ny), opp_a)
        if score > best[0]:
            best = (score, dx, dy)

    if best[1] or best[2]:
        return [best[1], best[2]]
    return [0, 0]