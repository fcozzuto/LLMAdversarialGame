def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        dx = 0 if sx >= w - 1 else 1 if sx <= 0 else 0
        dy = 0 if sy >= h - 1 else 1 if sy <= 0 else 0
        if dx == 0 and dy == 0:
            return [0, 0]
        return [dx if dx != 0 else 0, dy if dy != 0 else 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    prefs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    best_key = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds
        key = (-(gain > 0), -gain, ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in prefs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp_target = cheb(ox, oy, tx, ty)
        lead = d_opp_target - d_to_target
        mkey = (-(lead > 0), -lead, d_to_target, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]