def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    oppCorner = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    myCorner = min(corners, key=lambda c: man(sx, sy, c[0], c[1]))

    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = 2.0 * man(nx, ny, ox, oy) - 0.1 * man(nx, ny, myCorner[0], myCorner[1]) + 0.03 * man(nx, ny, oppCorner[0], oppCorner[1])
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a target resource where we are relatively closer than opponent
    best_r = None
    best_r_score = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        # Prefer: large (oppd - myd), then nearer overall, then deterministic tie
        s = (oppd - myd, -min(myd, oppd), -rx, -ry)
        if best_r_score is None or s > best_r_score:
            best_r_score = s
            best_r = (rx, ry)

    tx, ty = best_r

    def move_eval(dx, dy):
        nx, ny = sx + dx, sy + dy
        myd = man(nx, ny, tx, ty)
        oppd = man(nx, ny, ox, oy)

        # Also consider if opponent is closer to the best contested resource next
        best_cont = None
        for rx, ry in resources:
            mydn = man(nx, ny, rx, ry)
            oppdn = man(ox, oy, rx, ry)
            score = (opcdn := (oppdn - mydn), -mydn, -rx, -ry)
            if best_cont is None or score > best_cont:
                best_cont = score
        contested_gap = best_cont[0]  # opp closer advantage to opponent if positive

        # If opponent is threatening a resource (small/negative gap), prioritize distancing from opponent.
        # If we can win the target, go for it and avoid drifting too close to opponent.
        return (1.8 * myd - 2.2 * contested_gap) + (0.9 * oppd)

    # We want to minimize "move_eval"
    bestm = None
    bestv = None
    for dx, dy in sorted(moves):
        v = move_eval(dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]