def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # deterministic chase opponent corner-ish
        dx0 = 1 if ox > sx else (-1 if ox < sx else 0)
        dy0 = 1 if oy > sy else (-1 if oy < sy else 0)
        for ddx, ddy in [(dx0, dy0), (dx0, 0), (0, dy0), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    # choose target favoring resources I'm likely to reach first
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # reward if I'm closer than opponent; discourage if opponent is clearly closer
        val = (-myd) + (0.85 * (opd - myd))
        if myd == 0:
            val += 10**6
        if myd <= 1:
            val += 5
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # pick move that reduces distance to target; add small deterministic penalties
    best_m = (0, 0)
    best_s = -10**18
    opp_near = cheb(sx, sy, ox, oy) <= 2
    for mdx, mdy in dirs:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # base score: lower distance better
        s = -d * 10
        # prefer stepping on a resource if present
        if (nx, ny) in resources:
            s += 10**6
        # opportunistic: if opponent is near, don't drift toward them too much
        if opp_near:
            s -= cheb(nx, ny, ox, oy)  # farther is better (subtract smaller)
        # deterministic tie-break: prefer diagonal, then right, then up
        s += 0.01 * (1 if mdx != 0 and mdy != 0 else 0)
        s += 0.001 * (mdx + 1)  # -1->0,0->1,1->2
        s += 0.0001 * (mdy + 1)
        if s > best_s:
            best_s = s
            best_m = (mdx, mdy)

    return [best_m[0], best_m[1]]