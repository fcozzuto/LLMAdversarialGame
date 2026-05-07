def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    cand = []
    for dx0 in (-1, 0, 1):
        for dy0 in (-1, 0, 1):
            nx, ny = sx + dx0, sy + dy0
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx0, dy0, nx, ny))
    if not cand:
        return [0, 0]

    # If no resources, move toward opponent's start corner midpoint (stabilize).
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx0, dy0, nx, ny in cand:
            v = -cheb(nx, ny, tx, ty) - 0.05 * cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx0, dy0)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Deny heuristic: predict opponent's next step to the "best" resource for it,
    # and if we can step onto the same cell, prefer that.
    def next_step(px, py, rx, ry):
        dx = 0 if rx == px else (1 if rx > px else -1)
        dy = 0 if ry == py else (1 if ry > py else -1)
        return px + dx, py + dy, dx, dy

    opp_best = None
    opp_margin = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        m = od - sd
        if opp_margin is None or m > opp_margin or (m == opp_margin and od < cheb(ox, oy, opp_best[0], opp_best[1])):
            opp_margin = m
            opp_best = (rx, ry)
    deny_cell = None
    if opp_best is not None:
        nx2, ny2, _, _ = next_step(ox, oy, opp_best[0], opp_best[1])
        if inside(nx2, ny2) and (nx2, ny2) not in obstacles:
            deny_cell = (nx2, ny2)

    best_move = None
    best_val = None
    for dx0, dy0, nx, ny in cand:
        val = -10**9
        # Immediate deny
        if deny_cell is not None and (nx, ny) == deny_cell:
            val = 10**6
        # Resource race: maximize (opponent_distance - my_distance), then minimize my_distance
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            cur = margin * 1000 - sd
            # Slight preference to approach a resource closer to our current position (stable)
            cur += -0.1 * cheb(nx, ny, sx, sy)
            if cur > val:
                val = cur
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]