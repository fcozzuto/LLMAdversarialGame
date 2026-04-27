def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_for(x, y):
        if resources:
            best_res = 10**9
            for rx, ry in resources:
                d = abs(x - rx) + abs(y - ry)
                if d < best_res:
                    best_res = d
            res_term = -best_res * 3
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            res_term = -((x - cx) ** 2 + (y - cy) ** 2) ** 0.5

        opp_d = abs(x - ox) + abs(y - oy)
        opp_term = opp_d * 1.5
        return res_term + opp_term

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_for(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
        elif sc == best_sc and best is not None:
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best