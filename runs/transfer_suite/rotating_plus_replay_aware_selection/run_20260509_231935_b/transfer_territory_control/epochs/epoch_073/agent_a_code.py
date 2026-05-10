def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def to_set(x):
        s = set()
        if not x:
            return s
        for p in x:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    un_set = to_set(observation.get("unclaimed_cells"))
    res_set = to_set(observation.get("resources"))

    cx, cy = w // 2, h // 2

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    target = None
    if un_set:
        bestd = None
        for tx, ty in un_set:
            d = man(sx, sy, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (tx < target[0] or (tx == target[0] and ty < target[1]))):
                bestd = d
                target = (tx, ty)
    elif res_set:
        bestd = None
        for tx, ty in res_set:
            d = man(sx, sy, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (tx < target[0] or (tx == target[0] and ty < target[1]))):
                bestd = d
                target = (tx, ty)
    else:
        target = (cx, cy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy):
            continue
        if un_set and (nx, ny) in un_set:
            score = 100000
        else:
            d_t = man(nx, ny, target[0], target[1])
            d_o = man(nx, ny, ox, oy)
            score = -d_t * 100 + d_o * 10
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]