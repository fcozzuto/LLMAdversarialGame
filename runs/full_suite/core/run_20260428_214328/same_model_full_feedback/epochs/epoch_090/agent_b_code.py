def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(nx, ny, tx, ty):
        dx = nx - tx
        if dx < 0: dx = -dx
        dy = ny - ty
        if dy < 0: dy = -dy
        d = dx if dx > dy else dy  # Chebyshev
        return (d, (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))

    if res:
        best_t = res[0]
        best_d = None
        for tx, ty in res:
            dx = sx - tx
            if dx < 0: dx = -dx
            dy = sy - ty
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if best_d is None or d < best_d:
                best_d, best_t = d, (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w // 2), (h // 2)

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sm = score_move(nx, ny, tx, ty)
        if best is None or sm < best:
            best, best_move = sm, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]