def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

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
        return dx if dx > dy else dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))

    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = None
        bestScore = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            score = -d
            if bestScore is None or score > bestScore:
                bestScore, best = score, (dx, dy)
        return [best[0], best[1]]

    bestMove = cand[0]
    bestScore = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        # choose a target resource; encourage stealing (opp closer -> bad) and approaching ourselves
        sBest = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer resources where we are closer than opponent, and overall closeness
            score = (do - ds) * 3 - ds
            if sBest is None or score > sBest:
                sBest = score
        if bestScore is None or sBest > bestScore:
            bestScore, bestMove = sBest, (dx, dy)
    return [bestMove[0], bestMove[1]]