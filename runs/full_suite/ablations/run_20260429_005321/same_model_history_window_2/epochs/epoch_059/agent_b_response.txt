def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_adj_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1
        return pen

    if not resources:
        best_move = (0, 0)
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    target = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        closer = opd - myd  # positive means we are closer
        # Prefer resources we can reach first; punish ones opponent can reach sooner.
        score = closer * 100 - myd
        if opd < myd:
            score -= (myd - opd) * 60
        # Small tie-break to spread: prefer targets closer to our bottom-right-ish direction (towards mid).
        score += -(cheb(rx, ry, w - 1, h - 1) // 2)
        if score > best_score:
            best_score = score
            target = (rx, ry)

    rx, ry = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        od = cheb(nx, ny, ox, oy)
        pen = obstacle_adj_pen(nx, ny)
        # Primary: minimize distance to target; Secondary: maximize distance from opponent; Tertiary: avoid obstacles.
        val = -nd * 1000 + od * 10 - pen * 3
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]