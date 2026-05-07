def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", None)
    if not resources:
        candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = None
        bestv = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (best is None or (nx, ny) < best)):
                bestv = v
                best = (nx, ny)
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    best = None
    bestd = 10**9
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and ok(x, y):
                d = cheb(sx, sy, x, y)
                if d < bestd:
                    bestd = d
                    best = (x, y)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = -cheb(nx, ny, tx, ty) - 0.1 * cheb(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (nx, ny) < (sx + bestm[0], sy + bestm[1])):
            bestv = v
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]