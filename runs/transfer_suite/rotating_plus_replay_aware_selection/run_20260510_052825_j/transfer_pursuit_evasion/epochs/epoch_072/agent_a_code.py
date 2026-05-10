def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    obstacles = observation.get("obstacles") or []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def deg(x, y):
        c = 0
        for dx, dy in moves:
            if free(x + dx, y + dy):
                c += 1
        return c

    role = str(observation.get("self_role") or "").lower()
    purs = ("purs" in role) or ("pursuer" in role)

    if res:
        tx, ty = min(res, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        def score(nx, ny):
            return -(abs(nx - tx) + abs(ny - ty)) * 10 + deg(nx, ny)
    else:
        def score(nx, ny):
            d = abs(nx - ox) + abs(ny - oy)
            return (d if not purs else -d) * 10 + deg(nx, ny)

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best