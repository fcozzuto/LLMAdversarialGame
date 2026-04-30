def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    tx = ty = None
    if resources:
        best = None
        for rx, ry in sorted(resources):
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            score = (od - sd, -sd, -rx, -ry)  # maximize relative advantage, then closer
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1 + 0) // 2, (h - 1 + 0) // 2

    if sx == tx and sy == ty:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    want_dx = sign(tx - sx)
    want_dy = sign(ty - sy)
    candidates = []
    if want_dx or want_dy:
        candidates.append((want_dx, want_dy))
        if want_dx and want_dy:
            candidates.append((want_dx, 0))
            candidates.append((0, want_dy))
    candidates += [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]