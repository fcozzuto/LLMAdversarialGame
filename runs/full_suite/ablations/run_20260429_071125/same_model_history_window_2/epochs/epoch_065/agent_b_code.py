def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = (int(sp[0]), int(sp[1])) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (int(op[0]), int(op[1])) if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    best_target = (cx, cy)
    best_val = -10**18

    if resources:
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            val = (opd - myd) * 1000 - myd + (-(cheb(rx, ry, cx, cy)))
            if val > best_val:
                best_val = val
                best_target = (rx, ry)

    tx, ty = best_target
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = dist(nx, ny, tx, ty)
        opd2 = dist(ox, oy, tx, ty)
        score = (opd2 - myd2) * 1000 - myd2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not ok(sx + dx, sy + dy):
        for dx, dy in candidates:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [dx, dy]