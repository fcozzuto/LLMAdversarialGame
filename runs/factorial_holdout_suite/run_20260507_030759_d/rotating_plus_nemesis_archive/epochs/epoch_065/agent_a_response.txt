def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        ahead = 1 if myd < oppd else 0
        cand = (ahead, oppd - myd, -myd, tx, ty)
        if best is None or cand > best[0]:
            best = (cand, (tx, ty))

    tx, ty = best[1]
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    desired = (sx + dx0, sy + dy0)
    if 0 <= desired[0] < w and 0 <= desired[1] < h and desired not in obst:
        return [dx0, dy0]

    myd0 = cheb(sx, sy, tx, ty)
    best_step = (0, 0, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            myd1 = cheb(nx, ny, tx, ty)
            progress = myd0 - myd1
            if progress > best_step[2] or (progress == best_step[2] and (dx, dy) != (0, 0)):
                best_step = (dx, dy, progress)
    return [int(best_step[0]), int(best_step[1])]