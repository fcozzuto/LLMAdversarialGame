def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = ox, oy
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = cheb(nx, ny, tx, ty)
            if best is None or val > best[0] or (val == best[0] and (nx, ny) < best[1]):
                best = (val, (nx, ny), dx, dy)
        return [best[2], best[3]] if best else [0, 0]

    # Choose resource with best advantage (reach sooner than opponent), then move toward it.
    # Tie-break deterministically by resource coordinates.
    best_res = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer or at least not far behind; also prefer nearer overall.
        adv = do - ds
        val = (adv, -ds, -rx, -ry)
        if best_res is None or val > best_res[0]:
            best_res = (val, rx, ry)
    _, tr, tc = best_res

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds_next = cheb(nx, ny, tr, tc)
        do_now = cheb(ox, oy, tr, tc)
        # Primary: minimize our distance to target resource
        # Secondary: increase opponent's relative disadvantage (larger adv)
        # Tertiary: keep deterministic with coordinate tie-break
        val = (-ds_next, (do_now - ds_next), -nx, -ny)
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]