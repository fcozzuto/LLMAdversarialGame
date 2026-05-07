def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not res:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        for x, y in res:
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best[0]:
                best = (d, x, y)
        tx, ty = best[1], best[2]

    def step_toward(px, py, x, y):
        dx = 0 if x == px else (1 if x > px else -1)
        dy = 0 if y == py else (1 if y > py else -1)
        for cand in [(dx, dy), (dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]:
            ndx, ndy = cand
            nx, ny = px + ndx, py + ndy
            if valid(nx, ny):
                return [ndx, ndy]
        return [0, 0]

    return step_toward(sx, sy, tx, ty)