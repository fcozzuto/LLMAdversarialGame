def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not inb(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target selection: prefer resources where we can gain tempo vs opponent.
    if resources:
        best = None
        bestv = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Higher is better: beat opponent, but don't drift too far.
            v = (od - sd) * 10 - sd
            # Deterministic tie-break: smaller x then y then sd
            tb = (v, -(tx * 100 + ty), -sd)
            if best is None or (tb > bestv):
                best = (tx, ty)
                bestv = tb
        tx, ty = best
    else:
        # If no resources visible, move to center-ish to improve access next.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy step toward target with obstacle avoidance; also handle direct blockage.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer the ideal direction, then shortest distance to target, then deterministic tie-break.
        dir_pen = 0 if (dx == dx0 and dy == dy0) else 1
        candidates.append((dir_pen, d, nx * 100 + ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]