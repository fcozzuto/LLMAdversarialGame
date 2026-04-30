def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0: w = 8
    if h <= 0: h = 8
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best = None
    best_my = None
    best_op = None
    for rx, ry in resources:
        if (rx, ry) == (sx, sy):
            return [0, 0]
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        if myd <= (best_my if best_my is not None else 10**9) and (myd - opd) <= (best_my - best_op if best_op is not None else 10**9):
            if best is None or myd < best_my or (myd == best_my and opd < best_op):
                best = (rx, ry)
                best_my = myd
                best_op = opd

    if best is None and resources:
        best = min(resources, key=lambda r: dist(sx, sy, r[0], r[1]))

    if best is not None:
        rx, ry = best
        curd = dist(sx, sy, rx, ry)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                nd = dist(nx, ny, rx, ry)
                if nd < curd:
                    return [int(dx), int(dy)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny) and (nx, ny) != (sx, sy):
                return [int(dx), int(dy)]
        return [0, 0]

    curdo = dist(sx, sy, ox, oy)
    best_move = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            score = dist(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]