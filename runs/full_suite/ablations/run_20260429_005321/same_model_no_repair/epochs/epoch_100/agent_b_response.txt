def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        if (x, y) in obst:
            return 10**6
        r = 0
        for dx, dy in adj8:
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in obst:
                r += 2
        return r

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            my_d = None
            opp_d = None
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                if my_d is None or d1 < my_d:
                    my_d = d1
                if opp_d is None or d2 < opp_d:
                    opp_d = d2
            # Prioritize getting to a resource quickly and making it relatively less available to opponent.
            # Slightly prefer increasing distance from opponent when tied.
            v = -my_d + 0.6 * (opp_d - my_d) - 0.25 * cheb(nx, ny, ox, oy) - 0.75 * risk(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
            elif v == bestv:
                # deterministic tie-break: lexicographic on (dx,dy)
                if best is None or (dx, dy) < best:
                    best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No visible resources: move toward center while increasing separation from opponent and avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = -cheb(nx, ny, cx, cy) + 0.2 * cheb(nx, ny, ox, oy) - 0.75 * risk(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv and (best is None or (dx, dy) < best):
            best = (dx, dy)
    return [int(best[0]), int(best[1])]