def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except Exception:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except Exception:
        ox, oy = w - 1, h - 1

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                res.append((x, y))

    targets = res if res else [(ox, oy)]
    tx = tx2 = targets[0][0]
    ty = ty2 = targets[0][1]
    best = 10**9
    for x, y in targets:
        d = abs(sx - x) + abs(sy - y)
        if d < best:
            best = d
            tx2, ty2 = x, y

    ox, oy = tx2, ty2

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    def score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            return 10**12
        dist = abs(nx - ox) + abs(ny - oy)
        return dist

    best_move = (0, 0)
    best_score = 10**12
    for dx, dy in dirs:
        sc = score(dx, dy)
        if sc < best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]