def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = resources[0]
        bestd = man(sx, sy, tx, ty)
        for (x, y) in resources[1:]:
            d = man(sx, sy, x, y)
            if d < bestd:
                bestd, tx, ty = d, x, y
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            val = (d, abs(nx - ox) + abs(ny - oy))
            if best is None or val < best[0]:
                best = (val, [dx, dy])
        return best[1] if best is not None else [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    target = (cx, cy)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = (man(nx, ny, target[0], target[1]), -man(nx, ny, ox, oy))
        if best is None or val < best[0]:
            best = (val, [dx, dy])
    return best[1] if best is not None else [0, 0]