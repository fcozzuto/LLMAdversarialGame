def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = [(dx, dy) for dx, dy in moves if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            key = (d, abs(nx - ox) + abs(ny - oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    total = len(resources)
    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_resource_key = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Prefer resources where we are closer than opponent (opd - myd positive),
            # while still preferring nearer targets to avoid dithering.
            score_gap = opd - myd
            if total > 1:
                score_gap = score_gap * 10 - myd
            else:
                score_gap = score_gap * 20 - myd * 2

            # Safety: reduce likelihood of immediate collision/contest at same vicinity.
            safety = cheb(nx, ny, ox, oy)

            key = (-score_gap, myd, -opd, safety, rx, ry)
            if best_resource_key is None or key < best_resource_key:
                best_resource_key = key

        # Tie-break deterministically by position and move order
        key2 = (best_resource_key, nx, ny, dx, dy)
        if best_key is None or key2 < best_key:
            best_key = key2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]