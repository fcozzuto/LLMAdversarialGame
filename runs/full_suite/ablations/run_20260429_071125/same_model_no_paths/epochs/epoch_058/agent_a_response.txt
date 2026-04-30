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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Collect candidate resources
    candidates = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                myd = cheb(sx, sy, x, y)
                opd = cheb(ox, oy, x, y)
                # Prefer resources where we are closer than opponent (larger gap),
                # and then prefer larger distance advantage / closer to us.
                score = (opd - myd, -myd, x, y)
                candidates.append(((x, y), score))

    # Escape if stuck on blocked cell
    if (sx, sy) in blocked:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose target deterministically
    if candidates:
        candidates.sort(key=lambda t: (-t[1][0], t[1][1], t[1][2], t[1][3]))
        (tx, ty), _ = candidates[0]
    else:
        # No visible resources: drift toward center while staying safe
        tx, ty = (w // 2), (h // 2)

    # One-step greedy toward target, with simple tie-break and avoidance
    best = (10**9, 10**9, 0, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Tie-break: prefer staying still least; then lexicographic move preference
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (d, stay_pen, dx, dy)
        if key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]