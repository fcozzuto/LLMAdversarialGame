def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            sc = d
            if sc > best[2]:
                best = (dx, dy, sc)
        return [int(best[0]), int(best[1])] if best[2] > -10**8 else [0, 0]

    best_dx, best_dy, best_sc, best_myd = 0, 0, -10**18, 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_best = 10**18
        sc_best = -10**18
        # maximize advantage over opponent for a resource, then minimize my distance
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            advantage = opd - myd  # higher => I can arrive sooner
            # slight tie-break favoring resources that are "more mine" (bigger advantage) and closer
            sc = advantage * 100 - myd
            if sc > sc_best or (sc == sc_best and myd < my_best):
                sc_best = sc
                my_best = myd
        if sc_best > best_sc or (sc_best == best_sc and my_best < best_myd):
            best_sc, best_myd = sc_best, my_best
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]