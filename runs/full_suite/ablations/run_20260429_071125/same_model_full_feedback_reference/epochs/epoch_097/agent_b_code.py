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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Choose a target we can reach earlier than the opponent.
        best_t = None
        best_key = None
        for rx, ry in resources:
            d1 = man(sx, sy, rx, ry)
            d2 = man(ox, oy, rx, ry)
            # Prefer smaller (my advantage), then smaller my distance, then nearer to center (tie-break).
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = abs(rx - cx) + abs(ry - cy)
            key = (d1 - d2, d1, center_bias)
            if best_key is None or key < best_key:
                best_key, best_t = key, (rx, ry)

        tx, ty = best_t
        # Pick the move that improves advantage to the target.
        best_m = None
        best_m_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            myd = man(nx, ny, tx, ty)
            oppd = man(ox, oy, tx, ty)
            # Also bias slightly away from stepping into being late.
            key = (myd - oppd, myd, dx * dx + dy * dy, (nx - tx) + (ny - ty))
            if best_m_key is None or key < best_m_key:
                best_m_key, best_m = key, (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # No resources: deterministic survival/pressure towards center while keeping distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_m = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_center = man(nx, ny, cx, cy)
        dist_from_op = man(nx, ny, ox, oy)
        key = (-dist_from_op, my_center, dx, dy)
        if best_key is None or key < best_key:
            best_key, best_m = key, (dx, dy)
    return [int(best_m[0]), int(best_m[1])]