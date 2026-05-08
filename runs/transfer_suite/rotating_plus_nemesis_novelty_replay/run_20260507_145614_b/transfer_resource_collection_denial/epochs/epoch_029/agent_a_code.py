def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p[0], p[1]
            obs.add((int(x), int(y)))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for i, r in enumerate(resources):
        try:
            x, y = int(r[0]), int(r[1])
            res.append((x, y, i))
        except Exception:
            pass

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if w <= 0 or h <= 0:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        for ax, ay in dirs:
            nx, ny = sx + ax, sy + ay
            if valid(nx, ny):
                return [ax, ay]
        return [0, 0]

    best = None
    best_key = None
    for x, y, i in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        key = (od - sd, -sd, -i)  # maximize od-sd, then closer, then earlier index deterministically
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    pref = []
    for ax, ay in dirs:
        nx, ny = sx + ax, sy + ay
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        doopp = cheb(ox, oy, tx, ty)
        key = (-dself, doopp)  # choose smallest self distance to target; deterministic
        pref.append((key, ax, ay))
    if pref:
        pref.sort(key=lambda t: t[0])
        return [pref[0][1], pref[0][2]]

    return [0, 0]