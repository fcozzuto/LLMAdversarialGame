def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (0, 0)]

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                pen += 1
        return pen

    target = None
    best = None
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        lead = do - ds  # positive means we are closer
        pen = adj_obst_pen(x, y)
        # Prefer resources we can reach not much later than opponent, then closer, then safer.
        key = (- (lead > 0), -lead, ds, pen, (x + y), x, y)
        if best is None or key < best:
            best = key
            target = (x, y)

    if target is None:
        # Deterministic fallback: drift toward center while avoiding obstacles if possible.
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        d = cheb(nx, ny, tx, ty)
        # Tie-break: prefer moves that also reduce distance to opponent if we are behind (contest control).
        delta_to_opp = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
        key = (d, adj_obst_pen(nx, ny), delta_to_opp, (nx + ny), nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]