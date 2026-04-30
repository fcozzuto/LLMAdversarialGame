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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = (-(10**9), 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0]:
                best = (d, dx, dy)
        return [int(best[1]), int(best[2])]

    # Choose resource that maximizes capture advantage (closer than opponent).
    # Add deterministic side-bias that changes with turn parity to alter paths vs previous epoch.
    parity_bias = 1 if (int(observation.get("turn_index", 0) or 0) % 2 == 0) else -1
    bestR = None
    bestKey = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # higher means I'm relatively closer
        side = 1 if (rx - ry) * parity_bias >= 0 else -1
        key = (adv + 0.15 * side, -myd)  # maximize adv, then minimize myd
        if bestKey is None or key > bestKey:
            bestKey = key
            bestR = (rx, ry)

    tx, ty = bestR
    bestMove = None
    bestScore = None

    # Greedily move to reduce distance; if multiple, favor keeping advantage and blocking opponent path-ish.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd_my = cheb(nx, ny, tx, ty)
        nd_op = cheb(ox, oy, tx, ty)
        nd_adv = nd_op - nd_my
        # Prefer moves that also increase distance from opponent, but softly.
        score = (nd_adv, -nd_my, cheb(nx, ny, ox, oy))
        if bestScore is None or score > bestScore:
            bestScore = score
            bestMove = (dx, dy)

    if bestMove is None:
        return [0, 0]
    return [int(bestMove[0]), int(bestMove[1])]