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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    tx = ty = None
    if resources:
        best_cost = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cost = ds - 0.35 * (do - ds)  # prefer resources closer than opponent
            if best_cost is None or cost < best_cost or (cost == best_cost and (rx < tx or (rx == tx and ry < ty))):
                best_cost = cost
                tx, ty = rx, ry
    else:
        tx, ty = ox, oy  # no resources: move to contest center-ish via opponent direction

    # If we can pick it immediately, stay.
    if resources and (sx, sy) == (tx, ty):
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # primary: reduce distance to target
        d1 = cheb(nx, ny, tx, ty)
        # secondary: avoid moving toward opponent when we are equally distant
        d2s = cheb(nx, ny, ox, oy)
        # tertiary: deterministic tie-break
        val = (d1 * 1000 + d2s, (dx, dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]