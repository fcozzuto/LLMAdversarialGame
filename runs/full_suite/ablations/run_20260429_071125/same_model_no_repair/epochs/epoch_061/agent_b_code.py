def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    t = observation.get("turn_index", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = sorted([(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles])
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, cx, cy) + 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource deterministically
    best_r = None
    best_key = None
    for (rx, ry) in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if t % 2 == 0:
            key = (do - ds, -ds, rx, ry)  # pursue where we are ahead most
        else:
            key = (-do, ds, rx, ry)      # deny: where opponent is closest
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        d_to = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer reaching target sooner; slight preference for staying farther from opponent
        v = (-d_to, d_opp, dx, dy)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]