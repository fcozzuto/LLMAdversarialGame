def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if res:
        tx, ty = min(res, key=lambda r: (cheb(r[0], r[1], sx, sy), r[0], r[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dres = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        score = -dres
        if not res:
            score = dres - dopp
        else:
            score += 0.15 * dopp - 0.03 * (cheb(sx, sy, tx, ty) - dres)
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]