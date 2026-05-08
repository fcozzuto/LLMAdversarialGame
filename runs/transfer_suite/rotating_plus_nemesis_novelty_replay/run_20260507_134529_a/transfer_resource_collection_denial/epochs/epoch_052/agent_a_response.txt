def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = (0, 0, -10**18)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[2]: best = (dx, dy, v)
        return [best[0], best[1]]

    # Score each move by the best resource it can secure "earlier" than opponent, plus safety/progress terms.
    best = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        move_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # positive means we are closer; big gap is valuable
            gap = od - sd
            # progress: prefer lowering both our distance and opponent's distance
            prog = (-sd) + (-(od * 0.05))
            # encourage acting toward an actually reachable-ish cell (avoid staying too long)
            stay_pen = 0 if (dx != 0 or dy != 0) else -0.25
            v = gap * 2.0 + prog + stay_pen
            if v > move_best: move_best = v

        # tie-break deterministically: prefer smaller distance-to-opponent (often reduces intercept),
        # then prefer non-still, then lexicographic direction.
        if move_best > best[2]:
            best = (dx, dy, move_best)
        elif move_best == best[2]:
            dcur = cheb(nx, ny, ox, oy)
            dbest = cheb(sx + best[0], sy + best[1], ox, oy)
            if dcur < dbest:
                best = (dx, dy, move_best)
            elif (dx, dy) != (0, 0) and (best[0], best[1]) == (0, 0):
                best = (dx, dy, move_best)
            elif (dx, dy) < (best[0], best[1]):
                best = (dx, dy, move_best)

    return [best[0], best[1]]