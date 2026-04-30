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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        # No resources: block opponent by moving to squares that are "closer" to opponent than us, else drift.
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            d_opp = cheb(nx, ny, ox, oy)
            d_self = cheb(nx, ny, sx, sy)
            v = -d_opp + 0.05 * (d_self) + 0.01 * ((nx + 2 * ny) % 7) - 0.0001 * t
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Target: resource where our distance advantage over opponent is largest, with tie-break by closeness.
    best_target = None
    best_adv = -10**18
    for rx, ry in res:
        da = cheb(sx, sy, rx, ry)
        db = cheb(ox, oy, rx, ry)
        adv = (db - da)  # positive if we're closer
        # Slight preference to resources nearer to reduce time-to-capture
        score = adv * 10 + (-da) + (0.001 * ((rx + 3 * ry + t) % 11))
        if score > best_adv:
            best_adv = score
            best_target = (rx, ry)

    # If opponent is already closer to every resource, switch to minimizing opponent distance (contest) rather than chasing.
    any_positive = False
    for rx, ry in res:
        if cheb(sx, sy, rx, ry) < cheb(ox, oy, rx, ry):
            any_positive = True
            break

    center_x, center_y = (w - 1) // 2, (h - 1) // 2
    best = None
    bestv = -10**18

    for dx, dy, nx, ny in legal:
        d_to_center = cheb(nx, ny, center_x, center_y)
        d_to_opp = cheb(nx, ny, ox, oy)

        # Primary term: move toward chosen target if we have a real advantage somewhere; else "interfere".
        rx, ry = best_target
        d_to_target = cheb(nx, ny, rx, ry)
        v = 0.0

        if any_positive:
            v += 5.0 * (-d_to_target)
            # Bonus if this move keeps us at least as good as opponent for the target
            v += 1.2 * (cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)) * (-0.5)
            # Avoid allowing opponent to get much closer to the target next (proxy via current opponent distance)
            v += 0.15 * (-d_to_opp)
        else:
            # Contest: reduce opponent-to-target distance and keep our-to-target from getting worse
            v += 2.0 * (-cheb(ox, oy, rx, ry))
            v += 1.0 * (-d_to_target)
            v += 0.4 * (-abs(cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)))

        # Secondary: don't wander; prefer lower distance to any resource we might claim
        min_d_us = 10**9
        min_d_opp = 10**9
        for rxx, ryy in res:
            du = cheb(nx