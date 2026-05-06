def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    if not resources:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a resource that is not worse than opponent; if all are worse, pick least-worse.
    best_r = None
    best_sc = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources where we can be competitive; add small preference for not being too far.
        sc = (do - ds) * 20 - ds
        # Tie-break: prefer closer in Chebyshev (more diagonal-friendly)
        sc = sc - cheb(sx, sy, rx, ry)
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r
    # Intercept point: if opponent is closer, aim for a halfway point from opponent to target.
    ds0 = man(sx, sy, rx, ry)
    do0 = man(ox, oy, rx, ry)
    if do0 <= ds0:
        tx, ty = (ox + rx) // 2, (oy + ry) // 2
    else:
        tx, ty = rx, ry

    # Evaluate one-step moves using distance to chosen target, plus mild obstacle avoidance.
    best_move = (0, 0)
    best_val = -10**18
    dir_pref = [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in dir_pref:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = -man(nx, ny, tx, ty)
        # If we are close to target, slightly boost.
        v += 5 if cheb(nx, ny, rx, ry) <= 1 else 0
        # Discourage moving into tight spots: prefer having more legal neighbors.
        k = 0
        for adx, ady in moves:
            x2, y2 = nx + adx, ny + ady
            if legal(x2, y2):
                k += 1
        v += k * 0.25
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]