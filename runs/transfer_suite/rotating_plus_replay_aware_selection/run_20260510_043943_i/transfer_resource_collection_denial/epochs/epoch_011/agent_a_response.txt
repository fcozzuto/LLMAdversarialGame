def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_list = []
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs or not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if rx == ox or ry == oy:
            sweep_boost = 2
        else:
            sweep_boost = 0
        score = (od - sd) * 3 + sweep_boost * 2 - sd * 0.1
        res_list.append((score, sd, rx, ry))
    if not res_list:
        tx, ty = ox, oy
    else:
        res_list.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
        _, _, tx, ty = res_list[0]

    best = (-10**9, 0, 0)
    best_move = (0, 0)
    res_set = set(tuple(p) for p in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        gain = 8 if (nx, ny) in res_set else 0
        block = 2 if (nx == ox and ny == oy) else 0
        move_score = (opd - myd) * 2 + gain + block - (1 if (dx, dy) == (0, 0) else 0)
        tup = (move_score, myd, dx, dy)
        if tup > best:
            best = tup
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]