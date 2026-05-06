def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    # Heuristic: choose a move that maximizes your advantage (you closer than opponent) to the best resource,
    # with a small penalty for stepping toward obstacles.
    best = (-10**18, 0, 0)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            penalty = 10**6
        else:
            penalty = 0
            # penalty for having obstacles adjacent (discourage getting trapped)
            if (nx + 1, ny) in obs or (nx - 1, ny) in obs or (nx, ny + 1) in obs or (nx, ny - 1) in obs:
                penalty += 7

        # Score: best advantage among resources, also slightly prefer resources that are generally "safer" (far from obstacles).
        local_best = -10**18
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not inb(tx, ty) or (tx, ty) in obs:
                continue
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            # closer to you => higher (do - ds). If opponent is closer, try to flip it.
            adv = do - ds
            # small preference to avoid resources near obstacles
            near_obs = ((tx + 1, ty) in obs) or ((tx - 1, ty) in obs) or ((tx, ty + 1) in obs) or ((tx, ty - 1) in obs)
            if near_obs:
                adv -= 0.5
            # tie-breaker: prefer not-too-far overall for faster collection
            adv -= 0.01 * ds
            if adv > local_best:
                local_best = adv

        val = local_best - penalty
        if val > best[0]:
            best = (val, mx, my)

    return [best[1], best[2]]