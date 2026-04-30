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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; tie-break by being farther from opponent overall
            key = ((opd - myd) * 1000 - myd, myd, -(cheb(ox, oy, rx, ry)))
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No visible resources: move toward center (and away from opponent a bit)
        tx, ty = (w // 2, h // 2)

    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Also reduce opponent "effective pressure": favor moves that increase our distance from opponent-position
        dist_from_op = cheb(nx, ny, ox, oy)
        # Lexicographic: minimize distance to target, then maximize spacing from opponent, then deterministic dx/dy order
        val = (myd2, -dist_from_op, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]