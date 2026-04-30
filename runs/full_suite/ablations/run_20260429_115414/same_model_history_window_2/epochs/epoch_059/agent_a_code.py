def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_self = cheb(nx, ny, ox, oy)
            center = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            v = d_self * 3 + center
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick move that most improves our resource race (self closer than opponent), with tie-breaking by global leverage.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # mobility penalty: avoid moves that reduce available adjacent cells too much
        mob = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                mob += 1

        # resource race heuristic
        v = mob * 0.4
        best_res_v = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # positive when we are closer (or become closer), heavily discourage if opponent is already significantly nearer
            race = (do - ds)
            # prefer genuinely small ds too
            cand = race * 12 - ds
            # if we can match distance, slightly prefer nearer to prevent opponent snapping first
            if ds == do:
                cand -= 2
            if cand > best_res_v:
                best_res_v = cand
        # also add a small term for overall distance to "frontier" resources
        avg_ds = 0
        for rx, ry in resources:
            avg_ds += cheb(nx, ny, rx, ry)
        avg_ds /= len(resources)
        v += best_res_v + (-0.8 * avg_ds)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]