def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        def score(x, y):
            dres = 10**9
            tx = ty = None
            for rx, ry in resources:
                d = cheb(x, y, rx, ry)
                if d < dres:
                    dres, tx, ty = d, rx, ry
            dop = cheb(x, y, ox, oy)
            # Prefer closer to nearest resource; lightly prefer being farther from opponent.
            # Tie-break: prefer moves that also reduce distance to that chosen resource.
            dd = 0
            if tx is not None:
                dd = cheb(x, y, tx, ty) - cheb(sx, sy, tx, ty)
            return (-dres * 1000) + (dop * 25) + (-dd * 5)
    else:
        midx, midy = (sx + ox) // 2, (sy + oy) // 2
        def score(x, y):
            dop = cheb(x, y, ox, oy)
            dmid = cheb(x, y, midx, midy)
            return (-dmid * 1000) + (dop * 15)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]