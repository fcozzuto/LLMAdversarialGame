def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [7, 7]) or [7, 7]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, tx, ty) - 0.4 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target we can beat: maximize (opp_dist - self_dist), tie-break closer to resource.
    best_r = resources[0]
    best_margin = cheb(ox, oy, best_r[0], best_r[1]) - cheb(sx, sy, best_r[0], best_r[1])
    best_sd = cheb(sx, sy, best_r[0], best_r[1])
    for rx, ry in resources[1:]:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        if margin > best_margin or (margin == best_margin and sd < best_sd):
            best_margin, best_sd, best_r = margin, sd, (rx, ry)

    rx, ry = best_r

    # If opponent is about to take something first, pivot: chase that same resource only when it still keeps us competitive.
    # Otherwise, continue toward the best_r.
    opp_best = None
    opp_od = 10**9
    for r in resources:
        od = cheb(ox, oy, r[0], r[1])
        if od < opp_od:
            opp_od, opp_best = od, r
    if opp_best is not None:
        oi_r = cheb(sx, sy, opp_best[0], opp_best[1])
        if cheb(ox, oy, opp_best[0], opp_best[1]) - cheb(sx, sy, opp_best[0], opp_best[1]) <= 1:
            # Only override if we can still reduce their advantage by going there now.
            if cheb(sx, sy, rx, ry) > oi_r:
                rx, ry = opp_best

    # Take a