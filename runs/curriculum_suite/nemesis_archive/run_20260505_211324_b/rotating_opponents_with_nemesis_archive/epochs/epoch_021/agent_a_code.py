def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a + b

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def best_adv_for(posx, posy):
        myd = 10**9
        opnd = 10**9
        for rx, ry in res:
            d1 = md(posx, posy, rx, ry)
            if d1 < myd: myd = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < opnd: opnd = d2
        return myd, opnd

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        myd, opnd = best_adv_for(nx, ny)
        center = - (abs(nx - cx) + abs(ny - cy))
        val = (opnd - myd) * 1000 + center
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]