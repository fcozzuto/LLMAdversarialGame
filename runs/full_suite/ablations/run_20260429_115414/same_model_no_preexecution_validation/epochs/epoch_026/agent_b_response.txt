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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    if not res:
        # No visible resources: drift toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            d = cheb(nx, ny, tx, ty)
            edge = -abs(nx - tx) - abs(ny - ty)
            # small obstacle proximity penalty
            near = 0
            for ax in (nx-1, nx, nx+1):
                for ay in (ny-1, ny, ny+1):
                    if (ax, ay) in obs: near += 1
            v = edge - 2 * near - d * 0.1
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def obstacle_penalty(x, y):
        p = 0
        for ax in (x-1, x, x+1):
            for ay in (y-1, y, y+1):
                if (ax, ay) in obs: p += 1
        return p

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each possible move by contesting a target resource:
    # prefer resources where we can arrive sooner (or make opponent arrive later),
    # and among them prefer smaller self arrival time.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        my_best = -10**18
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # contest advantage: positive if we beat opponent to this resource
            adv = d_opp - d_self
            # if both can reach quickly, still prioritize nearer for self
            val = adv * 10 - d_self
            # slight preference to closer to opponent when we are behind (to reduce their gain)
            if adv < 0:
                val -= (cheb(nx, ny, ox, oy) * 0.25)
            # discourage paths that sit near obstacles
            val -= obstacle_penalty(nx, ny) * 1.5
            if val > my_best:
                my_best = val
        # extra tie-break: avoid staying adjacent to obstacles and avoid wasting moves
        waste = cheb(nx, ny, ox, oy) * 0.01
        if my_best - waste > best_val:
            best_val = my_best - waste
            best_move = (dx, dy)

    return [int(best