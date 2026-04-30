def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = None, None
    if resources:
        bestd = None
        best = None
        for x, y in resources:
            d = cheb(x, y, sx, sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_moves = []
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d = cheb(nx, ny, tx, ty)
            score = (d, -abs(nx - ox) - abs(ny - oy), nx, ny)
        else:
            d = cheb(nx, ny, tx, ty)
            score = (d, -abs(nx - ox) - abs(ny - oy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_moves = [(dx, dy)]
        elif score == best_score:
            best_moves.append((dx, dy))

    pick = best_moves[0]
    if len(best_moves) > 1:
        pick = sorted(best_moves)[(sx + sy) % len(best_moves)]
    return [int(pick[0]), int(pick[1])]