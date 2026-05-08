def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Move away from opponent if no resources (rare), else stay.
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise contest with smaller penalty.
        adv = (do - ds) - 0.15 * ds
        if (adv > best_adv) or (adv == best_adv and (ds < cheb(sx, sy, best_target[0], best_target[1]))):
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Aim to become closer to target than opponent, then generalize over nearby resources.
        val = (do2 - ds2) - 0.12 * ds2

        # Small hedge: if another resource becomes much more winnable, consider it.
        for j in (0, 1):
            if j >= len(resources):
                break
            rj = resources[(j + (rx + ry) % len(resources)) % len(resources)]
            rrx, rry = rj
            if (rrx, rry) == (rx, ry):
                continue
            v2 = (cheb(ox, oy, rrx, rry) - cheb(nx, ny, rrx, rry)) - 0.12 * cheb(nx, ny, rrx, rry)
            if v2 > val:
                val = 0.98 * val + 0.02 * v2
        if (val > best_val) or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]