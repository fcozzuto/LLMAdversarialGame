def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not res:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            dO = cheb(nx, ny, ox, oy)
            score = dO
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    corner_bias = cheb(sx, sy, w - 1, h - 1) - cheb(ox, oy, w - 1, h - 1)
    best_move = (0, 0, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue

        # obstacle proximity penalty
        opn = 0
        if obs:
            md = 99
            for px, py in obs:
                d = cheb(nx, ny, px, py)
                if d < md: md = d
                if md <= 0: break
            opn = 1.0 / (1.0 + md)

        dO = cheb(nx, ny, ox, oy)

        # For each resource, estimate "advantage" vs opponent reaching it
        best_adv = -10**9
        for rx, ry in res:
            dS = cheb(nx, ny, rx, ry)
            dA = cheb(ox, oy, rx, ry)
            # capture race: smaller dS is good, being able to beat opponent is better
            adv = (dA - dS)  # positive means we are closer this turn
            # slight preference for closer absolute distance
            val = adv * 3.0 - 0.4 * dS - 0.15 * cheb(rx, ry, w - 1, h - 1)
            if val > best_adv:
                best_adv = val

        # Also consider if moving towards opponent would deny/contest (if close, don't chase resources blindly)
        deny = 0.0
        if dO <= 3:
            deny = 1.5 * dO  # keep distance while still allowing contest

        # combine
        score = best_adv + 0.3 * corner_bias - 1.8 * opn + 0.05 * (dO if dO < 6 else 0) - 0.6 * (cheb(nx, ny, 0, 0))
        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [best_move[0], best_move[1]]