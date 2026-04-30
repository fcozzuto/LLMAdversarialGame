def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # If no resources: just move to reduce distance to center while staying safe
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -md(nx, ny, tx, ty)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    # Score a candidate position by best "edge" over opponent to any resource, with distance pressure
    def edge_score(px, py):
        best = -10**9
        for rx, ry in resources:
            myd = md(px, py, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Positive when we are closer than opponent for that resource
            v = (opd - myd) * 4 - myd
            if (px, py) == (rx, ry):
                v += 1000
            if v > best:
                best = v
        return best

    # Prefer moves with higher score; tie-break deterministically by direction order
    best_move = [0, 0]
    best_val = edge_score(sx, sy)  # allow "stay" baseline
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = edge_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]