def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also keep opponent further away.
            util = (d2 - d1) * 10 - d1
            # Mild tie-break toward closer resources.
            util -= (rx + ry) * 0.0001
            if best is None or util > best[0]:
                best = (util, rx, ry)
        _, tx, ty = best
    else:
        # No visible resources: drift toward center to create a better future position.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose a single step that improves our distance to target, while not helping opponent.
    best_move = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Also consider blocking: keep our move from moving closer to any resource we aren't targeting.
        block = 0
        for rx, ry in resources[:4]:
            if (rx, ry) != (tx, ty):
                if cheb(nx, ny, rx, ry) < cheb(sx, sy, rx, ry):
                    block += 0.5
        util = -myd * 3 + (od - cheb(ox, oy, tx, ty)) * 0 + block * (-1)
        # Deterministic tie-break by dir order via best_move comparison.
        if util > best_move[0]:
            best_move = (util, dx, dy)

    if best_move[0] == -(10**18):
        return [0, 0]
    return [best_move[1], best_move[2]]