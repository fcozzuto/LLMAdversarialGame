def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    opp_role = (observation.get("opponent_role", "") or "").lower()

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    prefer_row = 1.0 if "row" in opp_role else 0.0
    avoid_shadow = 0.6 if "shadow" in opp_role else 0.2

    best_t = None
    best_sc = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        align = 1.0 if (ry == sy or rx == sx) else 0.0
        block_ahead = 1.0 if (rx == ox and ry == oy) else 0.0
        sc = lead - 0.06 * ds + prefer_row * align - avoid_shadow * block_ahead
        if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best_t):
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = cheb(nx, ny, tx, ty)
            key = (d, abs(dx) + abs(dy), dx, dy)
            if best is None or key < best:
                best = key
                best_d = [dx, dy]
    if best_d is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                d = cheb(nx, ny, tx, ty)
                key = (d, abs(dx) + abs(dy), dx, dy)
                if best is None or key < best:
                    best = key
                    best_d = [dx, dy]
    return [int(best_d[0]), int(best_d[1])]