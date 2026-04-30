def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    if resources:
        best_move = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            myd = None
            opd = None
            key = None
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                # Prefer resources where we get there no later than opponent; then maximize advantage; then prefer closer.
                k = (0 if d1 <= d2 else 1, -(d2 - d1), d1, rx, ry)
                if key is None or k < key:
                    key = k
                    myd = d1
                    opd = d2
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward opponent if it helps blocking, else drift to center.
    tx, ty = (ox, oy)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    if cheb(sx, sy, tx, ty) > cheb(sx, sy, cx, cy):
        tx, ty = cx, cy
    best = None
    bestd = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        k = (d, dx, dy)
        if best_key := best is None:
            pass
        if bestd is None or k < best_key:
            bestd = d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]