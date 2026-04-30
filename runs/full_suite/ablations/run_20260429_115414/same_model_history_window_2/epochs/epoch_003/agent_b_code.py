def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set(tuple(p) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_resources = [tuple(r) for r in resources if tuple(r) not in blocked]
    if not valid_resources:
        tx, ty = (w - 1, h - 1) if ox < w // 2 else (0, 0)
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    opp_best = None
    for rx, ry in valid_resources:
        d = cheb(ox, oy, rx, ry)
        if opp_best is None or d < opp_best or (d == opp_best and (rx, ry) < opp_target):
            opp_best = d
            opp_target = (rx, ry)

    best = None
    best_me = None
    for rx, ry in valid_resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        gap = myd - oppd
        cand = (abs(gap), gap, myd, rx, ry)
        if best is None or cand < best:
            best = cand
            best_me = (rx, ry)

    tx, ty = best_me
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        k = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]