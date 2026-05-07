def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas_pref = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)]

    # Dynamic target: before midgame, prefer center line resources to fight row-sweep.
    mx, my = w // 2, h // 2
    time = observation.get("turn_index", 0)
    center_phase = (time < observation.get("turns_remaining", 0) - (w + h) // 2)

    best = None
    for rx, ry in resources:
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can arrive no later than opponent; break ties with closeness and progress upward.
        if do < ds:
            continue
        # Extra bias: in center phase, prefer resources near center; otherwise prefer "ahead" in y toward opponent's side.
        dcen = cheb(rx, ry, mx, my)
        ahead = (ry > sy) - (ry < sy)
        key = (0, ds, dcen if center_phase else 0, -ahead, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    if best is None:
        # Fallback: go to closest resource that isn't blocked, but avoid moving into immediate obstacles.
        target = (mx, my)
        bestd = cheb(sx, sy, target[0], target[1])
        for rx, ry in resources:
            if blocked(rx, ry):
                continue
            ds = cheb(sx, sy, rx, ry)
            if ds < bestd or (ds == bestd and (rx, ry) < target):
                bestd = ds
                target = (rx, ry)
    else:
        target = best[1]

    tx, ty = target
    # Choose move that reduces chebyshev distance; if tied, choose move that keeps us away from obstacles.
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            return (10**9, 10**9, 0)
        ns = cheb(nx, ny, tx, ty)
        # obstacle proximity (prefer safer positions)
        prox = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if inside(ax, ay) and blocked(ax, ay):
                    prox += 1
        # slight tie-break to match opponent sweep tendency: prefer increasing y when we can
        yprog = -(ny - sy)
        return (ns, prox, yprog)

    best_dm = None
    best_key = None
    for dx, dy in deltas_pref:
        k = score_move(dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_dm = (dx, dy)

    return [int(best_dm[0]), int(best_dm[1])]