def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        ahead = opd - myd  # positive means I'm closer
        if myd == 0:
            return 10**9
        # Prefer resources I'm closer to; otherwise still pursue slightly while not feeding opponent
        return ahead * 100 - myd - (0 if opd > myd else 50)

    if not resources:
        # Deterministic fallback: drift to center-ish while avoiding obstacles locally
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
    else:
        best = None
        bestv = -10**18
        for (rx, ry) in resources:
            v = score_target(rx, ry)
            if v > bestv:
                bestv = v
                best = (rx, ry)
            elif v == bestv and best is not None:
                if (rx, ry) < best:
                    best = (rx, ry)
        tx, ty = best

    # Pick move that minimizes distance to target, with deterministic tie-break and slight threat mitigation
    bestm = [0, 0]
    bestv = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # If tied on progress, discourage moving closer to opponent (helps contest resources)
        opd = cheb(nx, ny, ox, oy)
        v = (myd, opd, dx, dy)
        if v < (bestv if isinstance(bestv, tuple) else (bestv, 0, 0, 0)):
            bestv = v
            bestm = [dx, dy]

    return [int(bestm[0]), int(bestm[1])]