def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = w // 2
        ty = 0 if oy > sy else h - 1
        best = (10**9, 0, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            pref = abs(dx) + abs(dy)
            cand = (d, pref, dx, dy)
            if cand < best:
                best = cand
        if best[0] == 10**9:
            return [0, 0]
        return [best[2], best[3]]

    # Pick the resource where we are most likely to beat the opponent (largest adv = opp_dist - self_dist).
    best_r = None
    best_adv = None
    best_sd = None
    for p in resources:
        rx, ry = p[0], p[1]
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if best_r is None or adv > best_adv or (adv == best_adv and sd < best_sd):
            best_r = (rx, ry)
            best_adv = adv
            best_sd = sd

    tx, ty = best_r
    # Choose a one-step move minimizing distance to target, with slight bias away from obstacles.
    best = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Obstacle proximity penalty (deterministic, local).
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    pen += 1
        pref = abs(dx) + abs(dy)
        cand = (d, pen, pref, dx, dy)
        if cand < best:
            best = cand

    if best[3] == 0 and best[4] == 0 and (sx, sy) in obstacles:
        return [0, 0]
    if best[0] == 10**9:
        return [0, 0]
    return [best[3], best[4]]