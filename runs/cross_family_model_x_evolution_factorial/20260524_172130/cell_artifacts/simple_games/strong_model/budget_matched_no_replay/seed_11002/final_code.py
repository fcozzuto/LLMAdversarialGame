def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    def step(a, b):
        return (a > b) - (a < b)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (v[0], v[1])
        if isinstance(v, dict):
            for k in ("pos", "position", "loc", "location", "xy", "coord"):
                p = v.get(k)
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return (p[0], p[1])
        return None

    res = []
    r = observation.get("resources", [])
    if isinstance(r, dict):
        r = r.values()
    for x in r:
        p = pos(x)
        if p is not None:
            res.append(p)

    tx, ty = ox, oy
    if res:
        best = None
        bd = 10**9
        for x, y in res:
            d = abs(x - sx) + abs(y - sy)
            if d < bd or (d == bd and (x, y) < best):
                bd = d
                best = (x, y)
        tx, ty = best

    dx = step(tx, sx)
    dy = step(ty, sy)
    cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (1, 0), (-1, 0), (0, 1), (0, -1)]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if -1 < nx < w and -1 < ny < h and (nx, ny) not in obs:
            return [mx, my]
    return [0, 0]
