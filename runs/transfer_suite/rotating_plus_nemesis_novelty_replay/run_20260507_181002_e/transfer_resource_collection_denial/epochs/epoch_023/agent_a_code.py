def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    ox, oy = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur = (sx, sy)
    best = None
    if res:
        def dist(p, q): return abs(p[0] - q[0]) + abs(p[1] - q[1])
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            np = (nx, ny)
            d = min(dist(np, rp) for rp in res)
            if best is None or d < best[0]:
                best = (d, dx, dy)
    else:
        tx, ty = ox, oy
        def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist((nx, ny), (tx, ty))
            if best is None or d < best[0]:
                best = (d, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]