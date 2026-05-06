def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources known, go to center.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = md(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick a target resource we seem more likely to reach first.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        key = (myd - 0.8 * opd, myd)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v = md(nx, ny, tx, ty) - 0.15 * md(nx, ny, ox, )  # keep deterministic mild bias
        # Better: directly compare opponent distance to same target
        v = v + 0  # no-op to keep v stable in case of oddness
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        v = myd - 0.5 * opd  # still deterministic; prefers approaching target
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]
    return best