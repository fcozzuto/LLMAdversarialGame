def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(a, b, c, d):
        aa = a - c
        if aa < 0:
            aa = -aa
        bb = b - d
        if bb < 0:
            bb = -bb
        return aa + bb

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            score = man(nx, ny, tx, ty)
            if best is None or score < best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny))
        return [best[1][0] - x, best[1][1] - y] if best else [0, 0]

    target = None
    bestd = None
    for rx, ry in res:
        d = man(x, y, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)

    trx, try_ = target
    best = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, trx, try_)
        d_opp = man(nx, ny, ox, oy)
        on_res = 0 if (nx, ny) == (trx, try_) else 1
        score = d_self * 10 + on_res * 3 - d_opp
        cand = (score, -d_opp, d_self, nx, ny)
        if best is None or cand < best:
            best = cand

    return [best[3] - x, best[4] - y] if best else [0, 0]