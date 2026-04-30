def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obst.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    tx, ty = (w - 1, h - 1)
    if resources:
        bestd = None
        for p in resources:
            if not p or len(p) < 2:
                continue
            rx, ry = p[0], p[1]
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < (tx, ty)):
                bestd = d
                tx, ty = rx, ry
    else:
        # If no visible resources, drift to the more "forward" corner vs opponent
        if (ox + oy) < (sx + sy):
            tx, ty = 0, 0
        else:
            tx, ty = w - 1, h - 1

    def obstacle_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            nx = x + ax
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx, y + ay) in obst:
                    pen += 2
        return pen

    best = None  # (value, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dres = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        v = -10 * dres + 1.5 * dopp - 4 * obstacle_pen(nx, ny)
        # Tie-breaker: prefer larger dopp, then smaller dres, then earlier move order via iteration
        key = (v, dopp, -dres)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]