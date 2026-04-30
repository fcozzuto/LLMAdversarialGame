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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Walk toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best = min(best, (cheb(nx, ny, tx, ty), (dx, dy)))
        return list(best[1])

    # Determine best resource to contest using a deterministic "advantage" score
    # Prefer resources where we are not behind opponent (or least behind).
    bestR = None
    bestKey = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we can reach earlier or equal
        # Key: maximize adv, then closer distance for us, then lexicographic tie-break
        key = (-adv, ds, rx, ry)
        if bestKey is None or key < bestKey:
            bestKey = key
            bestR = (rx, ry)

    tx, ty = bestR

    # One-step lookahead: choose move that improves our priority resource while reducing opponent gain.
    bestMove = (0, 0)
    bestVal = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Higher is better: smaller myd, larger "reach gap" (opponent later), avoid moves that allow immediate opponent capture elsewhere
        # Also slight preference to move along direction toward target.
        moveDir = abs(nx - tx) + abs(ny - ty)
        oppCanTake = 0
        # Check if opponent could grab any other resource next turn; penalize if we move into a bad region by lowering minimal myd-to-any
        # Keep it small: only consider closest resource to opponent.
        for rx2, ry2 in resources:
            if (rx2, ry2) == (tx, ty):
                continue
            if cheb(ox, oy, rx2, ry2) <= 1:
                # If opponent is within 1 of a resource, prefer minimizing our distance to that same resource to contest
                if cheb(nx, ny, rx2, ry2) <= cheb(sx, sy, rx2, ry2):
                    oppCanTake += 1
        val = (opd - myd, -myd, -moveDir, -oppCanTake)
        if bestVal is None or val > bestVal:
            bestVal = val
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]