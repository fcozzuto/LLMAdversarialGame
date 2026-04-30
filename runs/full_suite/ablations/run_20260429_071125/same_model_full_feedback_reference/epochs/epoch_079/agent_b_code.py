def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        tx, ty = None, None
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            dres = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dres:
                    dres = d
            dob = cheb(nx, ny, ox, oy)
            val = dres * 100 + (7 - dob if dob < 7 else 0) + (0 if (nx, ny) == (sx, sy) else 0)
        else:
            val = cheb(nx, ny, tx, ty) * 100 + (7 - cheb(nx, ny, ox, oy) if cheb(nx, ny, ox, oy) < 7 else 0)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]