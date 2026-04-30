def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -((nx - cx) ** 2 + (ny - cy) ** 2)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return list(best if best is not None else (0, 0))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    alpha = 0.9
    best_move = (0, 0)
    best_score = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == sx and ny == sy:
            stay_pen = 0.15
        else:
            stay_pen = 0.0
        min_des = 10**30
        for rx, ry in resources:
            myd = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            opd = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            des = myd - alpha * opd
            if des < min_des:
                min_des = des
        center_bias = 0.003 * ((nx - cx) ** 2 + (ny - cy) ** 2)
        score = -min_des - center_bias - stay_pen
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]