def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0:
        w = 8
    if h <= 0:
        h = 8

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = 0, 0

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            try:
                resources.append((int(r[0]), int(r[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = (ox, oy)
    if resources:
        best = None
        bd = None
        for t in resources:
            if not inb(t[0], t[1]) or t in obs:
                continue
            d = dist((sx, sy), t)
            if bd is None or d < bd:
                bd = d
                best = t
        if best is not None:
            target = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        score = dist((nx, ny), target)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]