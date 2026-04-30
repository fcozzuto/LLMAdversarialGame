def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in set(resources):
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        d1 = a[0] - b[0]
        d2 = a[1] - b[1]
        if d1 < 0: d1 = -d1
        if d2 < 0: d2 = -d2
        return d1 if d1 >= d2 else d2

    if not resources:
        # deterministic fallback: drift away from opponent
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = cheb((nx, ny), (ox, oy))
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose the move that maximizes "racing advantage" to an individual best target resource,
    # and slightly penalizes moving closer to opponent relative to self.
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        self_d = cheb((nx, ny), (ox, oy))
        local_best = None
        local_bestv = None
        for r in resources:
            sd = cheb((nx, ny), r)
            od = cheb((ox, oy), r)
            # advantage: positive means we are closer than opponent
            adv = od - sd
            # also prioritize closer targets once advantage is comparable
            score = (adv * 1000) - sd
            if local_bestv is None or score > local_bestv:
                local_bestv = score
                local_best = r
        # tie-break: if multiple targets, prefer greater overall advantage and then farther from opponent
        v = local_bestv * 10 - self_d
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]