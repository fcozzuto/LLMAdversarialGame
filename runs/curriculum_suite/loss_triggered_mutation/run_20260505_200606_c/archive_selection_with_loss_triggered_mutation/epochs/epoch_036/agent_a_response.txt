def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def edge_dist(x, y):
        a = x
        b = w - 1 - x
        c = y
        d = h - 1 - y
        m = a if a < b else b
        m = c if c < d else d
        # compute min of four
        m1 = x if x < y else y
        m2 = (w - 1 - x) if (w - 1 - x) < (h - 1 - y) else (h - 1 - y)
        return m1 if m1 < m2 else m2

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best_adv = None
        best_r = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = opd - myd
            # prioritize winning races (adv), then shorter self distance
            if best_adv is None or adv > best_adv or (adv == best_adv and myd < md(sx, sy, best_r[0], best_r[1])):
                best_adv, best_r = adv, (rx, ry)
        tx, ty = best_r
        # if we're not ahead on the best target, bias toward a different reachable race
        if best_adv is not None and best_adv <= 0 and len(resources) > 1:
            alt_best_adv = best_adv
            alt_best_r = best_r
            for rx, ry in resources:
                myd = md(sx, sy, rx, ry)
                opd = md(ox, oy, rx, ry)
                adv = opd - myd
                if adv > alt_best_adv:
                    alt_best_adv, alt_best_r = adv, (rx, ry)
            tx, ty = alt_best_r

    best = None
    best_obj = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        adv = opd - myd
        # maximize race advantage, avoid edges, and reduce distance
        obj = 10 * adv + edge_dist(nx, ny) - myd
        if best_obj is None or obj > best_obj:
            best_obj = obj
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]