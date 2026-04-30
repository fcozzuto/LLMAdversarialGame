def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()
    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # drift to center and away from opponent a bit
            v = (3.5 - abs(nx - (w - 1) / 2)) + (3.5 - abs(ny - (h - 1) / 2)) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Prefer resources where we are (or become) closer than opponent.
    best = (0, 0)
    bestv = -10**18
    danger = cheb(sx, sy, ox, oy) <= 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best possible resource for this move; score based on lead and distance.
        cur = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive if we are closer than opponent now (after move)
            # Encourage grabbing: bigger lead and smaller absolute distance.
            val = 5 * lead - 0.25 * ds
            # If opponent is adjacent, reduce chasing that opponent can also instantly secure.
            if danger and do <= 1:
                val -= 4
            # Small tie-break: prefer staying closer to current resources set
            val += 0.02 * (len(resources) - abs(rx - sx) - abs(ry - sy))
            if val > cur:
                cur = val

        # Defensive component: avoid moving into positions that let opponent be too close to any resource.
        # Estimate worst-case for opponent if we move: where will opponent be relative to our best target?
        worst = 10**18
        for rx, ry in resources:
            do = cheb(ox, oy, rx, ry)
            if do < worst:
                worst = do
        # If we move without improving cur, prefer moves that increase our distance from opponent slightly.
        defens = -0.15 * cheb(nx, ny, ox, oy)

        v = cur + defens + 0.01 * (cheb(nx, ny, sx, sy) * 0) + 0.0 * worst
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]