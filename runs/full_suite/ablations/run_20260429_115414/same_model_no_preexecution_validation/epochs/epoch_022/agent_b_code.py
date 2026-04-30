def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_prox_pen(x, y):
        if not obs: return 0.0
        m = 99
        for px, py in obs:
            d = cheb(x, y, px, py)
            if d < m:
                m = d
                if m <= 1: break
        if m <= 1: return 3.0
        if m == 2: return 1.1
        return 0.0

    def legal(x, y): return inb(x, y) and (x, y) not in obs

    if not resources:
        # Fall back: move away from opponent and slightly toward board center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = cheb(nx, ny, ox, oy) * 1.2 - cheb(nx, ny, cx, cy) * 0.2 - obs_prox_pen(nx, ny) * 1.4
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource: prefer one we are closer to than opponent, else closest we can still contest.
    ordered = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive means we are closer
        ordered.append((advantage, ds, do, rx, ry))
    ordered.sort(reverse=True)
    target = None
    # Pick a resource we can reach no worse than opponent if possible
    for adv, ds, do, rx, ry in ordered:
        if ds <= do:
            target = (rx, ry)
            break
    if target is None:
        # Otherwise pick the resource with best combined desirability
        _, ds, do, rx, ry = ordered[0]
        target = (rx, ry)

    tx, ty = target
    # If opponent is adjacent, prioritize stepping away
    near_opp = cheb(sx, sy, ox, oy) <= 1

    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        v = -d_to_t * 1.4 + (2.5 if (nx, ny) == (tx, ty) else 0.0)
        v += d_opp * (2.2 if near_opp else 0.6)
        v -= obs_prox_pen(nx, ny) * 2.0
        # Mild tie-break: prefer staying off obstacle rows/cols by preferring exact cheb progress
        v += (0.05 if (d_to_t <= cheb(sx