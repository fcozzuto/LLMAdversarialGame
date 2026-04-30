def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def obs_adj(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles: c += 1
        return c
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    # If no resources remain, drift to center while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - 0.15 * obs_adj(nx, ny)
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    bestv = -10**18
    bestm = (0, 0)

    # Target resource: prioritize where we can gain (opponent farther than us).
    # Evaluate each move by resulting "advantage" and local obstacle safety.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        adv_best = -10**18
        me_closest = 10**18
        op_closest = 10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me  # positive => we are closer than opponent
            if adv > adv_best:
                adv_best = adv
                me_closest = d_me
                op_closest = d_op
            # secondary track for tie behavior
            elif adv == adv_best and (d_me < me_closest or (d_me == me_closest and d_op < op_closest)):
                me_closest = d_me
                op_closest = d_op

        # Extra preference: get closer to the best resource even if adv is similar.
        # Discourage stepping into obstacle-heavy areas; mildly prefer moving away from opponent if tied.
        v = 120.0 * adv_best - 2.0 * me_clclosest - 0.35 * obs_adj(nx, ny) + 0.05 * cheb(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]