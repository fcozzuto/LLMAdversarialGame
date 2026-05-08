def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if (sx, sy) in obs:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    best_key = None
    any_nonneg = False
    for rx, ry in res:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        margin = do - ds
        if margin >= 0:
            any_nonneg = True
        key = (1, margin, -ds, -do) if margin >= 0 else (0, -do, -ds, -margin)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if not any_nonneg:
        # force chase the opponent's nearest to enable interception
        rx, ry = min(res, key=lambda p: (dist(ox, oy, p[0], p[1]), dist(sx, sy, p[0], p[1])))
    else:
        rx, ry = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_e = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = dist(nx, ny, rx, ry)
        do2 = dist(ox, oy, rx, ry)
        # primary: widen the gap (prefer being closer than opponent)
        e1 = do2 - ds2
        # secondary: minimize own distance; tertiary: slight preference to move toward target
        e = (e1, -ds2, -dist(nx, ny, ox, oy))
        if best_e is None or e > best_e:
            best_e = e
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]