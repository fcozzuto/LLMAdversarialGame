def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    res = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    res_list = []
    for r in res:
        if r and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
    obs_set = set()
    for b in obs:
        if b and len(b) >= 2:
            obs_set.add((int(b[0]), int(b[1])))

    if (sx, sy) in obs_set:
        return [0, 0]
    if (sx, sy) in res_list:
        return [0, 0]

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest_res_dist(x, y):
        if not res_list:
            return 10**9
        d = 10**9
        for rx, ry in res_list:
            dd = man(x, y, rx, ry)
            if dd < d:
                d = dd
        return d

    cur_res_d = nearest_res_dist(sx, sy)
    cur_opp_d = man(sx, sy, ox, oy)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) in res_list:
            return [dx, dy]

        rd = nearest_res_dist(nx, ny)
        od = man(nx, ny, ox, oy)

        key = (rd, -od, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best