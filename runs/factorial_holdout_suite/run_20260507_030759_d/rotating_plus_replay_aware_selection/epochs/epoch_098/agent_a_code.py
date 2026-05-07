def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    if w <= 0 or h <= 0:
        return [0, 0]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int):
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0:
            dx = -dx
        dy = by - ay
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if res:
            dmin = None
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            dres = dmin if dmin is not None else 999999
            dopp = cheb(nx, ny, ox, oy)
            sc = (-dres * 1000) + (dopp * 3)
        else:
            dopp = cheb(nx, ny, ox, oy)
            sc = dopp
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]