def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    def norm_cells(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                    s.add((x, y))
                except:
                    pass
        return s

    obstacles = norm_cells(observation.get("obstacles"))
    targets = norm_cells(observation.get("unclaimed_cells"))
    if not targets:
        targets = norm_cells(observation.get("resources"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if targets:
            nearest = min(man(nx, ny, tx, ty) for (tx, ty) in targets)
            dist_self = man(nx, ny, sx, sy)
            dist_op = man(nx, ny, ox, oy)
            score = (1000 - nearest) + (-dist_op) - 0.01 * dist_self
        else:
            score = -man(nx, ny, ox, oy)

        score += 0.000001 * ((nx + 2 * ny) - (ox + 2 * oy))
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]