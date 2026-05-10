def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    tr = observation.get("turns_remaining", 0)
    remcnt = observation.get("remaining_resource_count", len(valid))
    few = (tr <= 6) or (remcnt <= 3)

    def best_value(px, py):
        bestv = None
        for rx, ry in valid:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            advantage = od - sd
            v = advantage * (6.0 if few else 3.2) - sd * (0.35 if few else 0.55)
            if sd == 0:
                v += 100.0
            elif sd == 1:
                v += 4.0
            if bestv is None or v > bestv[0]:
                bestv = (v, rx, ry)
        return bestv

    target = best_value(sx, sy)
    if target is None:
        return [0, 0]
    _, tx, ty = target

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist_to_target(nx, ny):
        return man(nx, ny, tx, ty)

    # One-step lookahead: prefer moves that maximize best_value.
    bestm = None
    for dx, dy, nx, ny in candidates:
        v2 = best_value(nx, ny)
        vv = v2[0]
        dd = dist_to_target(nx, ny)
        key = (vv, -dd, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, dx, dy)
    return [int(bestm[1]), int(bestm[2])]