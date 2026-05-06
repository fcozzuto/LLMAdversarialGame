def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def best_for_pos(px, py):
        if res:
            best = None
            for rx, ry in res:
                sd = cheb(px, py, rx, ry)
                od = cheb(ox, oy, rx, ry)
                key = (od - sd, -sd, -rx, -ry)
                if best is None or key > best[0]:
                    best = (key, (rx, ry))
            return best[1]
        return (ox, oy)

    target = best_for_pos(sx, sy)
    tx, ty = int(target[0]), int(target[1])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        nt = best_for_pos(nx, ny)
        ntx, nty = int(nt[0]), int(nt[1])
        sd = cheb(nx, ny, ntx, nty)
        od = cheb(ox, oy, ntx, nty)
        key = (od - sd, -sd, -ntx, -nty, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move