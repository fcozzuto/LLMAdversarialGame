def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist(a, b, c, d):  # Chebyshev
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if res:
        res_set = set(res)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny) and (nx, ny) in res_set:
                return [dx, dy]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if res:
            sd = min(dist(nx, ny, rx, ry) for rx, ry in res)
            od = min(dist(ox, oy, rx, ry) for rx, ry in res)
            # prefer smaller self distance and larger opponent distance
            score = (od - sd) * 100 - sd
        else:
            # no resources: drift away from opponent
            score = dist(nx, ny, ox, oy)
        key = (-score, nx - sx, ny - sy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]