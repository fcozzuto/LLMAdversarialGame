def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles", []) or []
    obst = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def dsq(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def best_target():
        if not res:
            return None
        best = None
        bestv = None
        for (rx, ry) in res:
            dse = dsq(sx, sy, rx, ry)
            doe = dsq(ox, oy, rx, ry)
            # Prefer targets where we are relatively closer than opponent, and nearer overall.
            v = (doe - dse) * 10 - dse
            if bestv is None or v > bestv or (v == bestv and (rx + ry) < (best[0] + best[1])):
                bestv = v
                best = (rx, ry)
        return best

    target = best_target()

    # If no resources visible, move toward board center deterministically.
    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd = None
        bestmove = (0, 0)
        for dx, dy, nx, ny in candidates:
            d = dsq(nx, ny, cx, cy)
            if bestd is None or d < bestd:
                bestd, bestmove = d, (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    tx, ty = target
    # One-step evaluation: maximize capture chance (we become closer than opponent) and reduce our distance.
    bestv = None
    bestmoves = []
    for dx, dy, nx, ny in candidates:
        dse = dsq(nx, ny, tx, ty)
        doe = dsq(ox, oy, tx, ty)
        v = (doe - dse) * 20 - dse
        if bestv is None or v > bestv:
            bestv = v
            bestmoves = [(dx, dy)]
        elif v == bestv:
            bestmoves.append((dx, dy))

    # Deterministic tie-break: prefer staying still, then smaller |dx|, then smaller |dy|, then lexicographic.
    def tkey(m):
        dx, dy = m
        return (0 if (dx == 0 and dy == 0) else 1, abs(dx), abs(dy), dx, dy)

    bm = sorted(bestmoves, key=tkey)[0]
    return [int(bm[0]), int(bm[1])]