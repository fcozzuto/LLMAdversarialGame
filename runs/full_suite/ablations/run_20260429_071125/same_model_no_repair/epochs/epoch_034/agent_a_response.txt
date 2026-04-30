def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # deterministic fallback: drift to center while avoiding obstacles
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            v = -cheb(nx, ny, tx, ty) - 0.01 * ((nx - sx) ** 2 + (ny - sy) ** 2)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # main: maximize distance-advantage over opponent for the best reachable resource;
    # if no lead is possible, switch to contesting by reducing my distance to opponent.
    best_overall, best_val = (0, 0), -10**18
    my_to_opp = cheb(sx, sy, ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # compute best lead across resources
        best_lead, best_finish = -10**9, 10**9
        any_lead = False
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd
            if lead > 0:
                any_lead = True
            # prefer bigger lead, then smaller myd (earlier capture), then smaller myd to finish tie-break
            if lead > best_lead or (lead == best_lead and myd < best_finish):
                best_lead, best_finish = lead, myd

        if any_lead:
            # strongly prefer immediate/large lead; slightly penalize being far from target
            v = best_lead * 20 - best_finish
        else:
            # no advantage: contest by reducing distance to opponent, and keep some progress toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            v = -cheb(nx, ny, ox, oy) * 10 - cheb(nx, ny, cx, cy) * 0.1 - 0.001 * (best_finish)

        # tiny deterministic preference for staying if tied, via movement penalty
        v -= 0.0001 * ((nx - sx) ** 2 + (ny - sy) ** 2)

        if v > best_val or (v == best_val and (dx, dy) == (0, 0)):
            best_val, best_overall = v, (dx, dy)

    return [best_overall[0], best_overall[1]]