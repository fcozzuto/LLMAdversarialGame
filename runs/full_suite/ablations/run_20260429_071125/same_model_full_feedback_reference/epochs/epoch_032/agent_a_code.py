def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        best = None
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = (abs(nx - ox) - abs(ny - oy))
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = 0
        d_self_min = 10**9
        d_opp_min = 10**9
        for x, y in resources:
            ds = abs(nx - x) + abs(ny - y)
            do = abs(ox - x) + abs(oy - y)
            if ds < d_self_min:
                d_self_min = ds
            if do < d_opp_min:
                d_opp_min = do
            if (nx, ny) == (x, y):
                val += 100000
        val += 2000 / (1 + d_self_min)
        val += 1000 * (d_opp_min - d_self_min) / (1 + d_self_min + d_opp_min)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]