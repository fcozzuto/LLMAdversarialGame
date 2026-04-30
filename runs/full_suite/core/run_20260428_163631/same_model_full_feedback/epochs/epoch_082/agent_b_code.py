def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm = (0, 0)
        bestv = (10**9, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            myd = cheb(nx, ny, cx, cy)
            oppd = cheb(nx, ny, ox, oy)
            v = (myd, -oppd)
            if v < bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    best_res = resources[0]
    best_gap = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        gap = oppd - myd  # maximize our tempo advantage
        if best_gap is None or gap > best_gap or (gap == best_gap and myd < cheb(sx, sy, best_res[0], best_res[1])):
            best_gap = gap
            best_res = (rx, ry)

    rx, ry = best_res
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd_next = cheb(nx, ny, rx, ry)
        # If opponent is closer to the same target, try to avoid enabling their contact:
        oppd_to_target = cheb(ox, oy, rx, ry)
        opp_dist_from_next = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to our chosen target.
        # Secondary: prefer keeping away from opponent.
        # Tertiary: if we're not winning tempo, prefer moves that increase opponent's distance from our target (proxy).
        proxy_opp = -abs(oppd_to_target - myd_next)
        score = (myd_next, -opp_dist_from_next, proxy_opp)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]