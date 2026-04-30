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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_move = None
        best_score = None
        for dx, dy, nx, ny in legal:
            my_best = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach sooner; tie-break toward closer and away from opponent.
                sc = (opd - myd) * 100 - myd
                sc += (myd == 0) * 1000
                if sc > my_best:
                    my_best = sc
            # Small tie-break: reduce distance to opponent to avoid being "passed"
            my_tie = -cheb(nx, ny, ox, oy)
            total = (my_best, my_tie)
            if best_score is None or total > best_score:
                best_score = total
                best_move = [dx, dy]
        return best_move

    # No visible resources: drift deterministically toward center while staying away from obstacles (already filtered)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestd = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, cx, cy)
        # Prefer moves that increase separation from opponent slightly
        td = cheb(nx, ny, ox, oy)
        total = (d, -td)
        if bestd is None or total < bestd:
            bestd = total
            best = [dx, dy]
    return best