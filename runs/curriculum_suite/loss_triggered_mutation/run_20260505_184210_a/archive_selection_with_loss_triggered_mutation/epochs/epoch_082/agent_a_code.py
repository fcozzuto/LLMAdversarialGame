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

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res = observation.get("resources") or []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2
    me = (sx, sy)
    opp = (ox, oy)

    target = (cx, cy)
    best = 10**9
    for t in resources:
        dme = man(me, t)
        dop = man(opp, t)
        if dme <= dop and dme < best:
            best = dme
            target = t
    if target == (cx, cy) and resources:
        best = 10**9
        for t in resources:
            dme = man(me, t)
            if dme < best:
                best = dme
                target = t

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = -man((nx, ny), (tx, ty)) - (0 if (nx, ny) != opp else 1)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]