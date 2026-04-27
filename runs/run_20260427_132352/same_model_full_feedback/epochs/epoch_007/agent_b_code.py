def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    tx, ty = None, None
    if resources:
        best = None
        for x, y in resources:
            if (x, y) in obst:
                continue
            d = cheb(sx, sy, x, y)
            # tie-break deterministically
            key = (d, x, y)
            if best is None or key < best[0]:
                best = (key, x, y)
        tx, ty = best[1], best[2]
    else:
        tx, ty = ox, oy

    # Try moves that reduce distance to target, avoid obstacles.
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d = cheb(nx, ny, tx, ty)
        key = (d, dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, dx, dy)

    if bestm is not None:
        return [int(bestm[1]), int(bestm[2])]

    # If all moves blocked, stay.
    return [0, 0]