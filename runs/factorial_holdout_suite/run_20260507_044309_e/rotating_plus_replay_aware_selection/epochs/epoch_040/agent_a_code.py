def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        bestv, bestm = None, [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty))
            if bestv is None or v < bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    bestv, bestm = None, [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # One-step lookahead: choose resource that maximizes reach advantage after this move.
        best_adv = None
        best_ds = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better
            # tie-break: finish sooner; then closer along same cheb
            key = (-(adv), ds, cheb(sx, sy, rx, ry))
            if best_adv is None or key < best_adv:
                best_adv = key
                best_ds = ds
        if best_adv is None:
            continue
        # Prefer higher advantage first; then reduce opponent incentive by keeping adv positive/stable.
        _, ds = best_adv[0], best_ds
        # Overall key: maximize advantage -> minimize -adv, then minimize own distance, then deterministic bias by coordinates.
        # Recompute adv for key stability:
        # (Using -best_adv[0] isn't exact since best_adv stored -(adv) as first.)
        adv_after = -best_adv[0]
        v = (-adv_after, ds, nx, ny)
        if bestv is None or v < bestv:
            bestv, bestm = v, [dx, dy]
    return bestm