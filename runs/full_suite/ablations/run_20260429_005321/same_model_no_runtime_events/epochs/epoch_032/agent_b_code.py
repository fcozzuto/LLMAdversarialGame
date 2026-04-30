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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        target = (ox, oy)
    else:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds) * 10 - ds  # prefer resources we are closer to
            if ds == 0:
                v += 10**6
            if v > bestv:
                bestv = v
                best = (rx, ry)
        target = best

    tx, ty = target

    # If opponent is about to take target and we can take/block it, prioritize
    if resources:
        dp = cheb(ox, oy, tx, ty)
        if dp <= 1:
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if inside(nx, ny) and (nx, ny) == (tx, ty):
                    return [dx, dy]

    # Choose step that best reduces distance to target; avoid moving toward opponent
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        # Encourage staying farther from opponent when close to target
        do2 = cheb(nx, ny, ox, oy)
        close = 1 if cheb(sx, sy, tx, ty) <= 2 else 0
        # Slightly penalize stepping onto squares adjacent to opponent to prevent contest flips
        adj_pen = 1 if cheb(nx, ny, ox, oy) == 1 else 0
        score = -ds2 * 100 + do2 * (20 if close else 5) - adj_pen * 30
        if (nx, ny) == (tx, ty):
            score += 10**7
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]