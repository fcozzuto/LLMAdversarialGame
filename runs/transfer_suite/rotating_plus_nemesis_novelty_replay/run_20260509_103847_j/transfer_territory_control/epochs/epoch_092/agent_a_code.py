def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = observation.get("resources") or []
    targets = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))

    if not targets:
        targets = [(ox, oy)]

    def best_score(nx, ny):
        d_best = 10**9
        for tx, ty in targets:
            dx, dy = nx - tx, ny - ty
            d = dx * dx + dy * dy
            if d < d_best:
                d_best = d
        d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        return d_best * 10 - d_op

    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = best_score(nx, ny)
        if sc < best[0]:
            best = (sc, dx, dy)

    if best[0] == 10**18:
        return [0, 0]
    return [int(best[1]), int(best[2])]