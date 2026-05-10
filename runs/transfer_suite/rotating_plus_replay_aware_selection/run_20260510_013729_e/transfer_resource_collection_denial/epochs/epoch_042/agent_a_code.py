def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # lead + quick capture, with tie-break favoring consistent ordering
        cap = 3 if (sx, sy) == (rx, ry) else 0
        score = (cap, (do - ds), -ds, -(do), -(rx * 8 + ry))
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # Try greedy toward target, else deterministic detour to maintain progress.
    candidates = [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0),
                  (0, 0), (1 if dx0 == 0 else -dx0, 0), (0, 1 if dy0 == 0 else -dy0)]
    seen = set()
    for dx, dy in candidates:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # Prefer moves that reduce distance to target; break ties by lead vs opponent
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        curds = cheb(sx, sy, tx, ty)
        # Accept immediately if it reaches/collects
        if (nx, ny) == (tx, ty):
            return [dx, dy]
        if ds2 < curds or (ds2 == curds and do2 >= cheb(sx, sy, ox, oy)):
            return [dx, dy]

    # If all blocked, stay still (engine will keep in place if invalid anyway).
    return [0, 0]