def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))
    res = observation.get("resources") or []
    resources = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            dd = d2(x, y, rx, ry)
            if best is None or dd < best[0] or (dd == best[0] and (rx, ry) < best[1]):
                best = (dd, (rx, ry))
        target = best[1]

    if target is None:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        bestmv = None
        bestv = None
        for dxm, dym in moves:
            nx, ny = x + dxm, y + dym
            if not ok(nx, ny):
                continue
            v = d2(nx, ny, cx, cy)
            if bestv is None or v < bestv or (v == bestv and (dxm, dym) < bestmv):
                bestv = v
                bestmv = (dxm, dym)
        return list(bestmv if bestmv is not None else (0, 0))

    tx, ty = target
    bestmv = None
    bestv = None
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not ok(nx, ny):
            continue
        v = d2(nx, ny, tx, ty)
        v += 0.01 * d2(nx, ny, ox, oy)  # small tie-break: prefer not to drift onto opponent
        if bestv is None or v < bestv or (v == bestv and (dxm, dym) < bestmv):
            bestv = v
            bestmv = (dxm, dym)
    return list(bestmv if bestmv is not None else (0, 0))