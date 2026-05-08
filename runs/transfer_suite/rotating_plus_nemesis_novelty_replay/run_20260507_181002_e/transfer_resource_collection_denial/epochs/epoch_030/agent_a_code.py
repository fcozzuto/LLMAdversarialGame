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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    neigh = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            neigh.append((nx, ny, dx, dy))
    if not neigh:
        return [0, 0]

    if not res:
        return [0, 0]

    self_near = min(res, key=lambda p: dist((sx, sy), p))
    opp_near = min(res, key=lambda p: dist((ox, oy), p))
    self_dn = dist((sx, sy), self_near)
    opp_dn = dist((ox, oy), opp_near)

    if opp_dn < self_dn:
        # Deny: move to reduce distance to opponent's nearest resource
        target = opp_near
        best = None
        for nx, ny, dx, dy in neigh:
            v = dist((nx, ny), target)
            if best is None or v < best[0] or (v == best[0] and dist((nx, ny), (ox, oy)) > best[1]):
                best = (v, dist((nx, ny), (ox, oy)), dx, dy)
        return [best[2], best[3]]
    else:
        # Lead: choose resource with maximal advantage (opp farther than us)
        def gain(p):
            sd = dist((sx, sy), p)
            od = dist((ox, oy), p)
            return (od - sd, -sd)
        target = max(res, key=gain)
        best = None
        for nx, ny, dx, dy in neigh:
            v = dist((nx, ny), target)
            if best is None or v < best[0] or (v == best[0] and dist((nx, ny), (ox, oy)) > best[1]):
                best = (v, dist((nx, ny), (ox, oy)), dx, dy)
        return [best[2], best[3]]