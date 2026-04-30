def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if any((sx == rx and sy == ry) for rx, ry in resources):
        return [0, 0]

    # Choose target resource: minimize distance; tie-break by smaller (x+y).
    best = None
    bestd = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if best is None or d < bestd or (d == bestd and (rx + ry) < (best[0] + best[1])):
            best = (rx, ry)
            bestd = d
    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                candidates.append((0, 0))
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Score closer to target; small preference for moving in chosen direction.
                dist = cheb(nx, ny, tx, ty)
                pref = 0
                if mx == dx:
                    pref += 1
                if my == dy:
                    pref += 1
                # Deterministic tie-break by coords.
                candidates.append((dist, -pref, nx, ny))
    if not candidates:
        return [0, 0]

    # Prefer exact direction move if possible
    direct = (sx + dx, sy + dy)
    if (dx != 0 or dy != 0) and 0 <= direct[0] < w and 0 <= direct[1] < h and direct not in obstacles:
        return [dx, dy]

    # Otherwise pick best candidate to target
    bestc = None
    for c in candidates:
        if c == (0, 0):
            continue
        if bestc is None or c < bestc:
            bestc = c
    if bestc is None:
        return [0, 0]
    _, _, nx, ny = bestc
    return [nx - sx, ny - sy]