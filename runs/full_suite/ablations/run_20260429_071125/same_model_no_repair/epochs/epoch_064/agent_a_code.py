def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    t = observation.get("turn_index", 0)
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        # Drift away from opponent while staying somewhat centered.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        if t % 2: cx = w - 1 - cx
        best, bestv = (0, 0), -10**18
        for dx, dy, nx, ny in legal:
            v = 1.1 * cheb(nx, ny, ox, oy) - 0.3 * cheb(nx, ny, cx, cy) - 0.01 * (nx + ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose target resource by "reach advantage": we want resources where (opp_dist - self_dist) is large.
    # Alternate between greedy advantage and slightly more conservative selection.
    prefer_adv = (t % 2 == 0)
    best_target, best_adv = None, -10**18
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        # Conservative mode: also prefer closer overall to avoid dithering.
        score = adv + (0.25 if prefer_adv else 0.05) * (-ds)
        if score > best_adv:
            best_adv, best_target = score, (rx, ry)

    tx, ty = best_target

    # Evaluate candidate moves: strongly prefer taking a resource, then reduce distance to target,
    # while also increasing distance from opponent (prevents easy steals).
    cur_on = (sx, sy) in res
    best, bestv = (0, 0), -10**18
    for dx, dy, nx, ny in legal:
        if (nx, ny) in res:
            v = 10**9
        else:
            ds_next = cheb(nx, ny, tx, ty)
            ds_cur = cheb(sx, sy, tx, ty)
            opp_next_dist = cheb(nx, ny, ox, oy)
            # Encourage progress to target; penalize moving away.
            progress = (ds_cur - ds_next)
            # Opponent pressure: sometimes prioritize separation more.
            sep_weight = 0.8 if (t % 3 == 0) else 0.45
            v = 3000 * progress + 20 * (-ds_next) + sep_weight * opp_next_dist - 0.01 * (nx + ny)
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]