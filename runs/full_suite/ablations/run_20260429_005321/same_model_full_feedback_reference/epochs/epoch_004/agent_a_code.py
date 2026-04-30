def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {tuple(p) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    if not resources:
        best = (0, 0, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = md(nx, ny, ox, oy)
            cand = (-d, dx, dy)
            if cand < best:
                best = cand
        _, dx, dy = best
        return [dx, dy]

    resources = [tuple(r) for r in resources]
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx, ry)  # maximize advantage (od-sd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        key = (nd - od, nd, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]