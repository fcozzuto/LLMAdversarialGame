def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    res = [(int(p[0]), int(p[1])) for p in resources]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_value(px, py):
        best = None
        for rx, ry in res:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            v = (opd - myd) * 1000 - myd
            t = -myd
            if best is None or (v, t) > best:
                best = (v, t)
        return best[0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Tie-breaking: prefer moves that reduce distance to the best target deterministically
    best_move = (None, -10**18)
    best_self = best_value(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        v = best_value(nx, ny)
        if v > best_move[1] or (v == best_move[1] and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0][0]) + abs(best_move[0][1]), best_move[0][0], best_move[0][1]) if best_move[0] is not None else True):
            best_move = ((dx, dy), v)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]