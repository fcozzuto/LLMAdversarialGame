def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestv:
                bestv = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    res_list = resources
    rem = int(observation.get("remaining_resource_count", len(res_list)) or len(res_list))
    w_anti = 0.9 if rem > 4 else 0.6
    w_race = 2.0 if rem > 4 else 3.0

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        mind = 10**9
        best_res = None
        for rx, ry in res_list:
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d
                best_res = (rx, ry)

        # race/deny: compare with opponent ability to reach the same target
        if best_res is None:
            race = 0
        else:
            rx, ry = best_res
            myd = mind
            opd = cheb(ox, oy, rx, ry)
            # prefer moves where we are closer; if opponent close, add slight danger
            race = (opd - myd)

        # also keep distance from opponent a bit
        pad = cheb(nx, ny, ox, oy)

        # rewards: collect quickly; then be faster than opponent
        v = (-w_race * mind) + w_anti * race + 0.03 * pad

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]