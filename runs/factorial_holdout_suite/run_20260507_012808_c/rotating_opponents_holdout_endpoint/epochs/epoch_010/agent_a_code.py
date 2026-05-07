def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, dict):
            x = p.get("x", p.get("posx", p.get("position", (None, None))[0]))
            y = p.get("y", p.get("posy", p.get("position", (None, None))[1]))
        else:
            try:
                x, y = p[0], p[1]
            except:
                continue
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in (observation.get("resources") or []):
        if isinstance(r, dict):
            x = r.get("x", r.get("posx", r.get("position", (None, None))[0]))
            y = r.get("y", r.get("posy", r.get("position", (None, None))[1]))
        else:
            try:
                x, y = r[0], r[1]
            except:
                continue
        if x is not None and y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    target = None
    if res:
        best = None
        for r in res:
            d = dist((sx, sy), r)
            if best is None or d < best[0] or (d == best[0] and r < best[1]):
                best = (d, r)
        target = best[1]

    def score(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            return -10**9
        s = 0
        if target is not None:
            s += 100 - dist((nx, ny), target) * 10
        dopp = dist((nx, ny), (ox, oy))
        s += -dopp * 2
        return s

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score(nx, ny)
        if sc > best_s:
            best_s = sc
            best_m = (dx, dy)

    dx, dy = best_m
    return [int(dx), int(dy)]