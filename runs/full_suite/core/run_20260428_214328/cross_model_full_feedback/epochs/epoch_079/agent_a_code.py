def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if res:
        # choose nearest resource (Chebyshev), tie by closer to opponent (to reduce their chance indirectly)
        best = None
        for r in res:
            d = dist((sx, sy), r)
            if best is None:
                best = (d, dist((ox, oy), r), r)
            else:
                bd, bo, _ = best
                nd = d
                nb = dist((ox, oy), r)
                if nd < bd or (nd == bd and nb < bo):
                    best = (nd, nb, r)
        tx, ty = best[2]
    else:
        # no visible resources: drift toward corner away from opponent deterministically
        tx, ty = (0, 0) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (w - 1, h - 1)

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_from_o = dist((nx, ny), (ox, oy))
        key = (d_to_t, -d_from_o, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]