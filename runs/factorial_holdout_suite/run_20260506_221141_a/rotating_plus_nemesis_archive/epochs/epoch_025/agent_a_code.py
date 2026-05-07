def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    res_list = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not inb(sx, sy):
        return [0, 0]

    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) or (x == sx and y == sy):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_op = dist((nx, ny), (ox, oy))
        d_best_res = min(dist((nx, ny), r) for r in resources)
        if best is None:
            best = (d_best_res, -d_op, dx, dy)
        else:
            cand = (d_best_res, -d_op, dx, dy)
            if cand < best:
                best = cand
    if best is None:
        return [0, 0]
    return [best[2], best[3]]