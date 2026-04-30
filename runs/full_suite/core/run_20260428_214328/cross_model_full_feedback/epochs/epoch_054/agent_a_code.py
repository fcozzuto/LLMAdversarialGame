def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y): obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))
    res = res[:]

    if res:
        best_r = None
        best_gap = None
        for rx, ry in res:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gap = opd - myd
            key = (gap, -myd, ry, rx)
            if best_r is None or key > best_key:
                best_r = (rx, ry); best_key = key
        tx, ty = best_r
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        score = (opd - myd, -myd, -cheb(nx, ny, ox, oy), ny, nx)
        if best is None or score > best_score:
            best = (dx, dy); best_score = score

    if best is None:
        for dx, dy in moves:
            nx = sx + dx; ny = sy + dy
            if inside(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]