def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        best_key = (-10**9, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            key = (d_opp, -cheb(nx, ny, ox, oy))
            if key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target we are comparatively closer to, but also not too "free" for opponent.
    best_t = None
    best_t_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: we want do - ds large, while not sending ourselves far.
        key = (do - ds, -ds, -((rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)), rx, ry)
        if best_t_key is None or key > best_t_key:
            best_t_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    cur_ds = cheb(sx, sy, rx, ry)
    # Greedy step toward target; if equal, keep distance from opponent.
    best = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (-nds, -cur_ds + nds, nds, d_opp, nx, ny)
        # Prefer moves that reduce distance to target; otherwise prefer maximizing opponent distance.
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]