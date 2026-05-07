def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def md(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if res:
        res = sorted(res)
        nearest = res[0]
        bestd = md(sx, sy, nearest[0], nearest[1])
        for rx, ry in res[1:]:
            d = md(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                nearest = (rx, ry)
    else:
        nearest = None

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        if nearest is None:
            val = md(nx, ny, ox, oy)
        else:
            dr = md(nx, ny, nearest[0], nearest[1])
            do = md(nx, ny, ox, oy)
            val = -dr * 1000 + do
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move