def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [7, 7]) or [7, 7]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # If stuck or no resources, drift toward center while increasing distance from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) + 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each move by best achievable "win margin" on any resource after our step.
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_future = 10**9
        my_adv_best = -10**18
        my_closeness = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            adv = opd - myd  # positive means we are closer than opponent
            # Slight preference for grabbing nearest resources once advantage exists.
            clos = -myd
            score = adv * 10.0 + clos * 0.6
            if score > my_adv_best:
                my_adv_best = score
                my_future = myd
                my_closeness = clos

        # Extra deterministic tie-breakers: avoid moving toward opponent; prefer not staying still.
        sep = cheb(nx, ny, ox, oy)
        still_pen = 0.05 if (dx == 0 and dy == 0) else 0.0
        toward_opp_pen = 0.12 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))  # discourage decreasing sep
        v = my_adv_best + 0.2 * sep + toward_opp_pen - still_pen

        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]