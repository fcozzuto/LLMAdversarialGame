def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for tx, ty in res:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        gap = opd - myd
        key = (gap, -myd, -(tx + ty))
        if best is None or key > best[0]:
            best = (key, tx, ty)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    for ndx in (-1, 0, 1):
        for ndy in (-1, 0, 1):
            nx, ny = sx + ndx, sy + ndy
            if ndx == 0 and ndy == 0:
                if (sx, sy) in obs:
                    continue
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                cand.append((ndx, ndy))

    if not cand:
        return [0, 0]

    best_move = None
    best_key = None
    for ndx, ndy in cand:
        nx, ny = sx + ndx, sy + ndy
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        gap2 = opd2 - myd2
        key = (gap2, -myd2, -(abs(tx - nx) + abs(ty - ny)), -(ndx * ndx + ndy * ndy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [ndx, ndy]
    return best_move if best_move is not None else [0, 0]