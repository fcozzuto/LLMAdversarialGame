def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer resources we can reach not later than opponent; otherwise still allow but penalize.
            # Deterministic tie-break by coordinates.
            margin = od - sd  # positive means we are closer/equal
            score = margin * 100 - sd
            key = (-(score), tx, ty)  # smaller key is better
            if best is None or key < best[0]:
                best = (key, tx, ty)
        tx, ty = best[1], best[2]

    # Move selection: choose valid move minimizing our distance to target,
    # while also (secondarily) maximizing the opponent's distance to that target.
    best_move = (10**9, -10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Secondary nudge: if we can advance, prefer diagonal/straight that reduces distance most.
        dist_delta = sd2 - cheb(sx, sy, tx, ty)
        key = (sd2, -od2, abs(dist_delta), dx, dy)
        if key < best_move:
            best_move = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]