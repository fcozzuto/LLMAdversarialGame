def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", None) or []
    obs_list = observation.get("obstacles", None) or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            sc = -dist((nx, ny), (cx, cy)) + 0.15 * dist((nx, ny), (ox, oy))
            key = (sc, -nx, -ny)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose a resource we can reach (and deny) sooner than opponent
    bestR = None
    for rx, ry in resources:
        r = (int(rx), int(ry))
        if r in obstacles:
            continue
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        if ds == 0:
            return [0, 0]
        # Prioritize positive gap and closeness; slight preference to avoid opponent proximity
        gap = do - ds
        sc = (gap * 10.0) + (1.5 / (1 + ds)) - (0.15 * do)
        key = (sc, -ds, -do, -r[0], -r[1])
        if bestR is None or key > bestR[0]:
            bestR = (key, r)
    target = bestR[1]

    # Move toward target; if ties, prefer reducing opponent's best access and staying safer
    best = None
    for dx, dy, nx, ny in legal:
        nds = dist((nx, ny), target)
        # Estimate how "deniable" target remains for opponent after this step
        ndo = dist((ox, oy), target)
        # Also consider if opponent could step closer to any nearby resource
        opp_safety = -dist((nx, ny), (ox, oy))
        sc = (-nds * 8.0) + (-(ndo - nds) * 0.3) + (0.02 * opp_safety)
        key = (sc, -nds, dist((nx, ny), (sx, sy)))
        if best is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]