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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    candidates = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    if not ok(sx, sy):
        for dx, dy in candidates:
            return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no advantage, just maximize distance from opponent
    if best is None or best_key[0] > 0:
        best_move = None
        best_val = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            val = cheb(nx, ny, ox, oy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best
    best_move = None
    best_dist = None
    best_tie = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        dist = cheb(nx, ny, tx, ty)
        tie = (abs((tx - nx)) + abs((ty - ny)))
        if best_dist is None or dist < best_dist or (dist == best_dist and tie < best_tie):
            best_dist = dist
            best_tie = tie
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]