def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    def near_obs_score(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestm, bestv = (0, 0), -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - 0.45 * near_obs_score(nx, ny)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Pick a target that we can reach relatively better than opponent.
    best_target = resources[0]
    best_rel = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = (do - ds)  # positive means we're closer
        # Small tie-break: prefer resources that are closer in absolute terms.
        rel = rel * 2 - 0.08 * (ds + do)
        if rel > best_rel:
            best_rel, best_target = rel, (rx, ry)

    rx, ry = best_target

    # If opponent is much closer to best target, pivot to next most "winnable".
    # (Meaningful strategic change vs just chasing one target.)
    ds0 = cheb(sx, sy, rx, ry)
    do0 = cheb(ox, oy, rx, ry)
    if do0 - ds0 >= 2 and len(resources) > 1:
        best2, best_rel2 = best_target, -10**18
        for a, b in resources:
            if (a, b) == (rx, ry):
                continue
            ds = cheb(sx, sy, a, b)
            do = cheb(ox, oy, a, b)
            rel = (do - ds) * 2 - 0.1 * (ds + do)
            if rel > best_rel2:
                best_rel2, best2 = rel, (a, b)
        rx, ry = best2

    bestm, bestv = (0, 0), -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_st = cheb(nx, ny, rx, ry)
        # Keep ourselves from stepping into situations where opponent can "steal" us.
        d_ot = cheb(ox, oy, rx, ry)

        # Interception pressure: prefer moves that reduce our distance more than theirs to the same target.
        rel_after = d_ot - d_st

        # Discourage getting closer to opponent directly (reduces collisions/turning their tempo).
        d_opp_now = cheb(nx, ny, ox, oy)
        d_opp_cur = cheb(sx, sy, ox, oy)

        # Prefer moving along decreasing distance to the target.
        delta_to_target = cheb(sx, sy, rx, ry) - d_st

        v