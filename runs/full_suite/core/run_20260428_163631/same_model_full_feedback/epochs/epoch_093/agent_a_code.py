def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    obs.discard((sx, sy))
    obs.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        score = (do - ds, ds, rx, ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = md(nx, ny, tx, ty)
            key = (-d, dx, dy)
            if bestm is None or key > bestm:
                bestm = key
                bestmove = [dx, dy]
    return bestmove