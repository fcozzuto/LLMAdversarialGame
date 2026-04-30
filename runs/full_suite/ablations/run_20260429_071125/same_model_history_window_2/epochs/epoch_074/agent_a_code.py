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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((x == sx and y == sy) for x, y in resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a target where we are relatively closer than opponent; deterministic tie-break by coordinates.
    bestT = None
    bestScore = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Favor (1) being closer, (2) shorter distance, (3) farther opponent, (4) earlier coordinate tie-break.
        score = (do - ds, -ds, do, -x, -y)
        if bestScore is None or score > bestScore:
            bestScore = score
            bestT = (x, y)

    if bestT is None:
        # No valid resources: drift toward center deterministically.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        tx, ty = bestT

    # Choose move minimizing our distance to target while maximizing opponent distance (and avoiding being too close).
    bestMove = [0, 0]
    bestVal = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        dTargetOpp = cheb(ox, oy, tx, ty)
        # Higher is better: want smaller ds2, larger do2; also slight preference if opponent is farther from target.
        val = (-ds2, dTargetOpp - cheb(ox, oy, tx, ty), do2, dx, dy)
        if bestVal is None or val > bestVal:
            bestVal = val
            bestMove = [dx, dy]

    return bestMove