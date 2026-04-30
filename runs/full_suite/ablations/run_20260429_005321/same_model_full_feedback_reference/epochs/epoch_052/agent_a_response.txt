def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = (d2(ox, oy, tx, ty) - d2(nx, ny, tx, ty)) + 0.01 * (nx - sx) + 0.005 * (ny - sy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    opp_d_self = d2(ox, oy, ox, oy)
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        beat = 1 if ds <= do else 0
        key = (-beat, ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = d2(nx, ny, rx, ry)
        no = d2(ox, oy, rx, ry)  # keep opponent position static for deterministic local policy
        adv = (no - ns)  # higher is better: we are closer than opponent to target
        dist_center = d2(nx, ny, (w - 1) // 2, (h - 1) // 2)
        v = adv + 0.001 * (-(dist_center)) + 0.0001 * (-(abs(nx - ox) + abs(ny - oy)))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]