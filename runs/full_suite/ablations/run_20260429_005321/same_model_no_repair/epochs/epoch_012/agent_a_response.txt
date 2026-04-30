def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = do - ds  # positive if we are closer
            # Prefer winning races, then faster reach, then closer resources with tie-break
            key = (-ahead, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = (w - 1, h - 1)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        # Obstacle avoidance: penalize moves adjacent to obstacles
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj_obs += 1
        # Prefer moves that increase advantage; if neutral, minimize distance; slight bias to progress to target
        score = (-adv, myd, adj_obs, (tx - nx if tx != nx else 0), (ty - ny if ty != ny else 0))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked, stay put (engine will keep position anyway)
    return [best_move[0], best_move[1]]