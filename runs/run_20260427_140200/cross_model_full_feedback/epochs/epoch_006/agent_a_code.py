def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    ti = int(observation.get("turn_index", 0))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # deterministic rotation/tie-break
    k = ti % 9
    moves = moves[k:] + moves[:k]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def obs_pen(x, y):
        # mild penalty for being adjacent/near obstacles
        p = 0
        for (ox2, oy2) in obstacles:
            d = abs(x-ox2) + abs(y-oy2)
            if d == 0:
                return 10**6
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    if not resources:
        # deterministic: move to maximize distance from opponent while keeping safe
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = md((nx, ny), (ox, oy)) - 2 * obs_pen(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return [best[0], best[1]]

    # choose the next position that maximizes our estimated advantage on some resource
    my = (sx, sy)
    opp = (ox, oy)
    best = [0, 0]
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # evaluate best resource for this next position
        best_here = -10**18
        for rx, ry in resources:
            myd = md((nx, ny), (rx, ry))
            oppd = md(opp, (rx, ry))
            # primary: advantage (we closer than opponent); secondary: avoid letting opponent also be close
            adv = (oppd - myd)
            # if tie, prefer closer resource; also discourage giving opponent a better advantage next
            sc = 20 * adv - myd - 0.5 * (adv < 0) - 0.1 * (oppd - myd)
            if sc > best_here:
                best_here = sc
        sc = best_here - 2 * obs_pen(nx, ny)
        # slight deterministic bias to not always "stare" at same direction
        sc += 0.01 * (dx - dy)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]