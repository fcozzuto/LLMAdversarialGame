def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or []) if tuple(p) not in obst]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obst_pen(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                if (x + ax, y + ay) in obst:
                    p += 2
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            p += 0.5
        return p

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        # Go toward a deterministic safe-ish center direction
        tx, ty = w // 2, h // 2
        best = (0, 0, -10**9)
        for dx, dy, nx, ny in valid:
            d = cheb(nx, ny, tx, ty)
            v = -d - obst_pen(nx, ny)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Race-the-nearest: choose move that maximizes advantage (opponent arrival - my arrival) to some resource.
    best = (0, 0, -10**18)
    for dx, dy, nx, ny in valid:
        my_best = 10**18
        opp_best = 10**18
        # Evaluate the resource that gives best advantage
        best_adv = -10**18
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            # tiny tie-break to prefer nearer resources to me
            if adv > best_adv or (adv == best_adv and md < my_best):
                best_adv = adv
                my_best = md
                opp_best = od
        # Encourage also moving closer to the overall best resource
        v = best_adv * 10 - my_best - 0.3 * obst_pen(nx, ny) + 0.01 * opp_best
        if v > best[2]:
            best = (dx, dy, v)

    return [best[0], best[1]]