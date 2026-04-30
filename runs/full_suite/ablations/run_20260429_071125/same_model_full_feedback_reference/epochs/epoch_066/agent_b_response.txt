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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (0, 0)
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    chosen = None
    best_score = None
    # Deterministic tie-break: prefer smaller (dx,dy) in lexicographic order after scoring
    for dx, dy in sorted(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Base: aim for best reachable resource
        local_best = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If opponent is closer, penalize taking that target
            # Margin scales with distance so we still consider blocked targets late-game.
            closeness_pen = 0
            if opd + 0 < myd:
                closeness_pen = 6 * (myd - opd)
            # If resource is at current position next to us, strongly prefer
            capture_bonus = -20 if myd == 0 else 0
            val = myd + closeness_pen + capture_bonus
            if val < local_best:
                local_best = val
        # Secondary: keep some pressure toward opponent by reducing cheb to them slightly
        pressure = 0.15 * cheb(nx, ny, ox, oy)
        score = local_best + pressure
        if best_score is None or score < best_score:
            best_score = score
            chosen = (dx, dy)

    return [chosen[0], chosen[1]]