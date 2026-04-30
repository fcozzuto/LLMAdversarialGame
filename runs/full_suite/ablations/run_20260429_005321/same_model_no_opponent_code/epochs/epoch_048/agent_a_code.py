def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_move(target):
        tx, ty = target
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d1 = cheb(nx, ny, tx, ty)
            d2 = cheb(nx, ny, ox, oy)
            val = (d1, -d2)
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]

    if not resources:
        best = [0, 0]
        bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd or (d == bestd and [dx, dy] < best):
                bestd = d
                best = [dx, dy]
        return best

    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if best_key is None or (myd <= opd and (best_key[2] > opd or best_key[0] > myd)):
            pass
        key = (0 if myd <= opd else 1, myd, opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    return best_move(best_target)