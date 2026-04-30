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
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return list(best[1] if best[1] is not None else (0, 0))

    # Choose a target resource where we are relatively closer than opponent.
    bestT = None
    bestScore = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Score: prioritize immediate/sooner wins, then avoid letting opponent be closer.
        # Small deterministic tie-break by coordinates.
        score = (myd - opd, myd, tx + ty)
        if bestScore is None or score < bestScore:
            bestScore = score
            bestT = (tx, ty)
    tx, ty = bestT

    # Greedy step toward target, with obstacle avoidance and tie-break by improving advantage.
    best = None
    bestTuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = myd - opd  # lower is better
        # Slight preference for progress (smaller myd), then stable preference for reducing distance from center.
        cd = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        cand = (adv, myd, cd, tx + ty, dx, dy)
        if bestTuple is None or cand < bestTuple:
            bestTuple = cand
            best = (dx, dy)
    return list(best if best is not None else (0, 0))