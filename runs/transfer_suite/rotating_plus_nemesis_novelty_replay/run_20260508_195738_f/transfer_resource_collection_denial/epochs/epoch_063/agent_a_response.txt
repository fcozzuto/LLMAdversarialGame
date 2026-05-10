def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy) - cheb(c[0], c[1], sx, sy))
        best = -10**9
        bestm = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
            if val > best:
                best, bestm = val, [dx, dy]
        return bestm

    # One-step lookahead: pick move maximizing our guaranteed lead over opponent for some resource.
    best_val = -10**18
    best_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Lead advantage over opponent for the most favorable resource (bigger is better).
        lead = -10**9
        tie_seek = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer or equal
            if adv > lead:
                lead = adv
                tie_seek = ds
            elif adv == lead and ds < tie_seek:
                tie_seek = ds
        # Extra term to reduce risk of being "denied": prefer smaller our distance among equal leads.
        risk = tie_seek
        # Micro-intercept: also encourage moving toward a resource that is currently closer to opponent (to contest).
        contest = min(cheb(nx, ny, rx, ry) + 0.001 * cheb(ox, oy, rx, ry) for rx, ry in resources)
        val = 1000 * lead - risk + 0.1 * (-contest)
        if val > best_val:
            best_val = val
            best_moves = [[dx, dy]]
        elif val == best_val:
            best_moves.append([dx, dy])

    # Deterministic tie-break: smallest (dx,dy) lexicographically.
    best_moves.sort(key=lambda m: (m[0], m[1]))
    return best_moves[0]