def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Target selection: prefer resources we can reach sooner; otherwise choose best "sabotage" (deny) via proximity.
    def best_target_from(x, y):
        if not resources:
            return (cx, cy), 0.0
        best = None
        for rx, ry in resources:
            myd = cheb(x, y, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we are not faster, still consider targets where we can arrive closer soonably (deny).
            # Key weights designed to change policy from pure distance-following: incorporate opponent threat and centrality.
            adv = (opd - myd)  # positive means we are closer
            central = -(abs(rx - cx) + abs(ry - cy))
            tie = -myd
            k = (adv * 3 + central, adv, tie)
            if best is None or k > best[0]:
                best = (k, (rx, ry))
        return best[1], best[0][0]

    target, _ = best_target_from(sx, sy)

    # If opponent is extremely close to our chosen target, pivot to a secondary target (material change).
    tx, ty = target
    if resources:
        myd0 = cheb(sx, sy, tx, ty)
        opd0 = cheb(ox, oy, tx, ty)
        if opd0 <= myd0 + 0:  # opponent not slower
            best2 = None
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                myd = cheb(sx, sy, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                k = ((opd - myd) * 3 - myd - (abs(rx - cx) + abs(ry - cy)))
                if best2 is None or k > best2[0]:
                    best2 = (k, (rx, ry))
            if best2 is not None:
                target = best2[1]
                tx, ty = target

    best_move = (0, 0)
    best_score = None

    # One-step lookahead scoring: move that best improves advantage to the chosen target, while not walking into opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        # Avoid giving opponent an immediate capture corridor: penalize moves that get too close to them.
        opp_gap = man(nx, ny, ox, oy)
        opp_pen = 0
        if opp_gap <= 2:
            opp_pen = -5 + opp_gap  # stronger when very close
        # Mild preference to reduce distance to target (stability).
        dist_pen = -myd * 0.5
        score = adv * 4 + opp_pen + dist_pen

        # Deterministic tie-breaker: prefer staying closer to our side center, then lexicographic move order.
        center_tie = -(abs(nx - cx) + abs(ny - cy)) * 0.01
        score = score + center_tie
        if