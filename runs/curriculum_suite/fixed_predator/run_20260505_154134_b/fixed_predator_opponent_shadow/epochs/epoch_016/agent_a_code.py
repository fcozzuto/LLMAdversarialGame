def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Build deterministic candidate targets: some nearest to us, some where we are behind.
    scored = []
    for r in resources:
        cx, cy = r
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        scored.append((self_d - opp_d, self_d, opp_d, cx, cy))
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    candidates = []
    for i in range(min(5, len(scored))):
        candidates.append((scored[i][3], scored[i][4]))
    # Add a couple resources where we are most behind to enable interception.
    scored2 = sorted(scored, key=lambda t: (-t[0], t[1], t[3], t[4]))
    for i in range(min(3, len(scored2))):
        c = (scored2[i][3], scored2[i][4])
        if c not in candidates:
            candidates.append(c)

    best_move = [0, 0]
    best_val = -10**18
    best_tie = (10**9, 10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate: maximize lead (opp_d - self_d), with slight preference for reducing our distance.
        local_best = -10**18
        for cx, cy in candidates:
            self_d2 = cheb(nx, ny, cx, cy)
            opp_d2 = cheb(ox, oy, cx, cy)
            lead = opp_d2 - self_d2
            # If opponent can take it sooner, we value blocking lead more.
            val = lead * 100 - self_d2
            if val > local_best:
                local_best = val
        tie = (abs(nx - ox) + abs(ny - oy), abs(nx - candidates[0][0]) + abs(ny - candidates[0][1]) if candidates else 0)
        if local_best > best_val or (local_best == best_val and tie < best_tie):
            best_val = local_best
            best_tie = tie
            best_move = [dx, dy]

    return best_move