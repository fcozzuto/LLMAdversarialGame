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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        bestd = None
        for rx, ry in resources:
            d = md(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best:
                best = key
                bestd = d
        tx, ty = resources[resources.index((best[1], best[2]))] if (best[1], best[2]) in resources else (best[1], best[2])
        tx, ty = int(tx), int(ty)
    else:
        tx, ty = ox, oy
        tx = 2 * sx - tx
        ty = 2 * sy - ty

    bestmv = (0, 0)
    bestval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = md(nx, ny, tx, ty)
        oppd = md(nx, ny, ox, oy)
        val = (v, -oppd, dx, dy)
        if bestval is None or val < bestval:
            bestval = val
            bestmv = (dx, dy)

    if ok(sx + bestmv[0], sy + bestmv[1]):
        return [int(bestmv[0]), int(bestmv[1])]
    for dx, dy in moves:
        if ok(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]