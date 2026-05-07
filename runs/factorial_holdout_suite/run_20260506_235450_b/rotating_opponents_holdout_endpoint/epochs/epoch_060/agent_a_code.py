def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            try:
                x, y = int(a.get("x")), int(a.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            try:
                x, y = int(r.get("x")), int(r.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None
    for x, y in res:
        d1 = cheb(sx, sy, x, y)
        d2 = cheb(ox, oy, x, y)
        key = (d1 - d2, d1, x, y)
        if best_val is None or key < best_val:
            best_val = key
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer getting closer; tie-break deterministically
        k = (d, dx, dy)
        if bestk is None or k < bestk:
            bestk = k
            bestm = [dx, dy]

    if bestm is None:
        return [0, 0]
    return bestm