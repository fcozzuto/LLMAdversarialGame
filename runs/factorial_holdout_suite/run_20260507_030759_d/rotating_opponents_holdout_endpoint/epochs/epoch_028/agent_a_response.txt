def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))

    if not res:
        return [0, 0]

    # Choose resource with maximal advantage (self closer than opponent), with small preference to nearer.
    best = None
    best_val = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If same row/col as opponent, slightly reduce (denier may contest line moves)
        line_pen = 0
        if ty == oy:
            line_pen += 1
        if tx == ox:
            line_pen += 1
        # Advantage: large when self significantly closer
        val = (od - sd) * 10 - sd - line_pen
        key = (val, -(sd), -(abs(tx - sx) + abs(ty - sy)), tx, ty)
        if best is None or key > best:
            best = key
            best_val = (tx, ty)

    tx, ty = best_val
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try preferred diagonal first; if blocked, try axis-aligned alternative; else stay.
    steps = [(dx, dy)]
    if dx != 0 and dy != 0:
        steps.append((dx, 0))
        steps.append((0, dy))
    else:
        if dx != 0:
            steps.append((dx, 0))
            steps.append((0, dy))
        else:
            steps.append((0, dy))
            steps.append((dx, 0))
    steps.append((0, 0))

    for mx, my in steps:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny):
            return [mx, my]
    return [0, 0]