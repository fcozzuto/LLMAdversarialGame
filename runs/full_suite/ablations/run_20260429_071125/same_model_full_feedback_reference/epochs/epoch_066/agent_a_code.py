def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    target = None
    if res:
        best = None
        for rx, ry in res:
            our = cheb(sx, sy, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            val = our - opp
            if best is None or (val < best) or (val == best and (our, rx, ry) < (best_our, best_rx, best_ry)):
                best = val
                best_our, best_rx, best_ry = our, rx, ry
        target = (best_rx, best_ry)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target is None:
            score = 0
        else:
            rx, ry = target
            ourd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            score = (ourd - opd, ourd, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]