def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2): return abs(x1-x2) + abs(y1-y2)

    # If no resources, just drift away from opponent to avoid contest pressure.
    if not resources:
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = md(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Heuristic: pick move that maximizes "resource advantage" and minimizes opponent threat.
    # Advantage to a resource = (opp_dist - my_dist), scaled by resource distance urgency.
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        my_to_opp = md(nx, ny, ox, oy)
        # Threat discourages moves that let opponent immediately sit on/near us.
        threat = -2.0 / (1 + my_to_opp)
        urgency = 0.0
        adv = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; also prefer nearer ones.
            a = (opd - myd) - 0.15 * myd
            if a > adv:
                adv = a
        # Bonus if already on a resource (should be game-managed by engine).
        on_resource = 1.0 if (nx, ny) in set(resources) else 0.0
        v = adv + threat + 0.5 * on_resource
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]