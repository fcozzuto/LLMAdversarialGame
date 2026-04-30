def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Deterministic target: choose resource minimizing (my dist, -opp advantage, x, y)
        best = None
        bestk = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            k = (myd, -(opd - myd), rx, ry)
            if bestk is None or k < bestk:
                bestk = k
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        myd = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance to current target
        val = -myd

        # If resources exist, consider second-best objective: avoid stepping into opponent's immediate capture zone
        # (deterministic "threat" penalty)
        threat = cheb(nx, ny, ox, oy)
        if threat <= 1:
            val -= 6

        # Also avoid giving opponent a closer approach to our target
        oppd = cheb(ox, oy, tx, ty)
        if cheb(ox, oy, tx, ty) < cheb(nx, ny, tx, ty):
            val -= 1

        # Small deterministic tie-break: prefer moves closer to target in x then y
        val += -(abs((nx - tx)) * 0.01 + abs((ny - ty)) * 0.001)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]