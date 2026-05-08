def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Flee to maximize distance from opponent
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

    # Pick target resource with best contest advantage (account for time)
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are closer, strongly prefer; otherwise penalize less when opponent also far
        score = (do - ds) * 2.0 - 0.35 * ds + 0.08 * do
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r
    cur_ds = cheb(sx, sy, rx, ry)
    # Choose a move that reduces our distance to target; tie-break by increasing opponent distance,
    # and by improvement in the best overall contest score among resources from the next step.
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        nds = cheb(nx, ny, rx, ry)
        if nds > cur_ds + 0:  # allow equal, avoid worse
            pass
        # Estimate contest for next position using same heuristic (cheap, small list)
        nxt_best = -10**18
        for rr in resources:
            r2x, r2y = rr
            dss = cheb(nx, ny, r2x, r2y)
            dpo = cheb(ox, oy, r2x, r2y)
            sc = (dpo - dss) * 2.0 - 0.35 * dss + 0.08 * dpo
            if sc > nxt_best:
                nxt_best = sc
        opp_dist = cheb(nx, ny, ox, oy)
        v = (cur_ds - nds) * 3.0 + (opp_dist) * 0.03 + nxt_best * 0.6
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then stay
        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]