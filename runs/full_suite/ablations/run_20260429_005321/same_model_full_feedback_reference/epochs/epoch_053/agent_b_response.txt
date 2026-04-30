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
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -d2(nx, ny, tx, ty) + d2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose a resource to contest: prefer close to self, far from opponent.
    best_t = resources[0]
    best_tv = -10**18
    for (rx, ry) in resources:
        v = -d2(sx, sy, rx, ry) + d2(ox, oy, rx, ry)
        if v > best_tv or (v == best_tv and (rx, ry) < best_t):
            best_tv, best_t = v, (best_t[0], best_t[1])
    tx, ty = best_t

    opp_t = min(resources, key=lambda r: d2(ox, oy, r[0], r[1]))
    oxr, oyr = int(opp_t[0]), int(opp_t[1])

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v_self = -d2(nx, ny, tx, ty)
        v_opp = d2(nx, ny, ox, oy)
        v_block = -d2(nx, ny, oxr, oyr)
        v = v_self + (v_opp // 2) + (v_block // 3)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]