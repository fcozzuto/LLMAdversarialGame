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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    if not resources:
        best = (10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_opp = cheb(nx, ny, ox, oy)
            d_self = cheb(nx, ny, w - 1 - ox, h - 1 - oy)
            # Prefer moving toward center/away from corner dead-ends.
            cand = (d_to_opp, d_self, dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]] if best[2] or best[3] else [0, 0]

    best_score = (-10**9, 10**9, 10**9, 0, 0)
    # score: maximize advantage (oppd - myd) to the best resource after move; tie-break by myd then by oppd
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_best = 10**9
        opp_best = 10**9
        adv_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - myd
            if adv > adv_best or (adv == adv_best and (myd < my_best or (myd == my_best and oppd < opp_best))):
                adv_best = adv
                my_best = myd
                opp_best = oppd
        # Add small preference to avoid getting too close behind opponent (contest slightly, not chase)
        contest = 0
        if adv_best >= 0:
            contest = cheb(nx, ny, ox, oy) // 4
        score = (adv_best, -my_best, -opp_best, contest, dx, dy)
        # Convert to comparable tuple where higher score is better; use negative where needed
        cand = (score[0], score[1], score[2], -score[3], score[4], score[5])
        if cand > best_score:
            best_score = cand

    return [int(best_score[4]), int(best_score[5])] if (best_score[4] or best_score[5]) else [0, 0]