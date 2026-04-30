def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if resources:
        # Deterministic target: best for us considering opponent pressure
        bestt = None
        bestt_key = None
        for tx, ty in resources:
            myd = kdist(sx, sy, tx, ty)
            opd = kdist(ox, oy, tx, ty)
            # Prefer closer; if close, prefer where we are relatively ahead; tie-break by coordinates
            key = (myd - opd, myd, tx, ty)
            if bestt is None or key < bestt_key:
                bestt = (tx, ty)
                bestt_key = key
        tx, ty = bestt
    else:
        tx, ty = cx, cy

    # New policy: maximize chance to arrive first; also lightly prefer central squares
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = kdist(nx, ny, tx, ty)
        opd = kdist(ox, oy, tx, ty)
        # Higher is better
        val = (opd - myd) * 10 - myd - 0.05 * kdist(nx, ny, cx, cy)
        # Tie-break deterministically by preferring smaller dx/dy lexicographically after val
        key = (-val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]