def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role)
    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, (list, tuple)):
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                    res_list.append((x, y))

    if res_list:
        tx, ty = min(res_list, key=lambda r: (sx - r[0]) * (sx - r[0]) + (sy - r[1]) * (sy - r[1]))
    else:
        if evader and not pursuer:
            tx, ty = (0, 0)
            bestd = -1
            for x in range(w):
                for y in range(h):
                    if (x, y) in obs_set:
                        continue
                    d = (sx - x) * (sx - x) + (sy - y) * (sy - y)
                    if d > bestd:
                        bestd = d
                        tx, ty = x, y
        else:
            tx, ty = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def score(nx, ny):
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if evader and not pursuer:
            od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            return (d * -1, od)
        if pursuer and not evader:
            od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            return (d * -1, od * -1)
        return (d * -1, 0)

    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best