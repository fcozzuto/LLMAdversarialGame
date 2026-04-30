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

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cd(nx, ny, tx, ty)
            if best is None or v < best[0] or (v == best[0] and (dx, dy) < best[1]):
                best = (v, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Choose a resource where we are likely closer than the opponent, using distance difference.
    best_r = None
    best_gap = None
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        gap = od - sd  # positive means we're closer or will arrive sooner
        if best_gap is None or gap > best_gap or (gap == best_gap and (rx, ry) < best_r):
            best_gap = gap
            best_r = (rx, ry)
    tx, ty = best_r

    # Move that improves our distance to target while also not letting opponent gain too much.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cd(nx, ny, tx, ty)
        opd = cd(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Also add a small term that prefers moves that reduce our distance to opponent (deny).
        deny = -cd(nx, ny, ox, oy) * 0.01
        # Primary: minimize my distance; Secondary: maximize (op - my) gap; Tie-break by direction.
        score = (myd, -(opd - myd), deny)
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    return list(best[1]) if best else [0, 0]