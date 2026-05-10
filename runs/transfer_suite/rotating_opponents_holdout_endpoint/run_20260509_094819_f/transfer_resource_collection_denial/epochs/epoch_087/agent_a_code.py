def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        return [0, 0]

    best = None
    for tx, ty in res:
        key = (man(sx, sy, tx, ty), man(ox, oy, tx, ty), tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            cand.append((man(nx, ny, tx, ty), dx, dy, nx, ny))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]