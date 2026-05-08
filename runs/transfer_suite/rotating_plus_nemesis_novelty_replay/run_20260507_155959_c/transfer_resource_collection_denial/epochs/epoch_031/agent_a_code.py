def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def legal_moves():
        m = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    m.append((dx, dy))
        return m

    moves = legal_moves()
    if not moves:
        return [0, 0]

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if res:
        def md(ax, ay, bx, by):
            d = ax - bx
            if d < 0:
                d = -d
            e = ay - by
            if e < 0:
                e = -e
            return d + e

        best = None
        best_key = None
        for rx, ry in res:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (od - sd, -sd, -(rx + ry), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def md1(dx, dy):
        nx, ny = sx + dx, sy + dy
        d = nx - tx
        if d < 0:
            d = -d
        e = ny - ty
        if e < 0:
            e = -e
        return d + e

    best_move = None
    best_md = None
    for dx, dy in moves:
        d = md1(dx, dy)
        key = (d, dx, dy)
        if best_md is None or key < (best_md, best_move[0], best_move[1]):
            best_md = d
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]