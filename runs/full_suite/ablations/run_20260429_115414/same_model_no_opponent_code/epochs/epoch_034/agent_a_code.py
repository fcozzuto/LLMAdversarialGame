def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (w - 1, h - 1)) or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best = None
    if res:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            bestd = None
            for rx, ry in res:
                d = abs(nx - rx) + abs(ny - ry)
                if bestd is None or d < bestd:
                    bestd = d
            cand = (bestd, abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is not None:
            return [best[4], best[5]]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            cand = (d, nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is not None:
            return [best[3], best[4]]

    return [0, 0]