def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    res = []
    for c in observation.get("resources") or []:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if ok(x, y):
                res.append((x, y))

    tx, ty = None, None
    if res:
        best = None
        for x, y in res:
            d = abs(x - sx) + abs(y - sy) - 0.2 * (abs(x - ox) + abs(y - oy))
            if best is None or d < best:
                best = d
                tx, ty = x, y
    else:
        ut = (observation.get("unclaimed_cells") or [])
        best = None
        for c in ut:
            if c is not None and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if ok(x, y):
                    d = abs(x - (w // 2)) + abs(y - (h // 2))
                    if best is None or d < best:
                        best = d
                        tx, ty = x, y
        if tx is None:
            tx, ty = w // 2, h // 2

    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        block = 0
        if (nx, ny) in obs:
            block = 10**6
        opp_close = abs(ox - nx) + abs(oy - ny)
        score = block + dist - 0.05 * opp_close
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move