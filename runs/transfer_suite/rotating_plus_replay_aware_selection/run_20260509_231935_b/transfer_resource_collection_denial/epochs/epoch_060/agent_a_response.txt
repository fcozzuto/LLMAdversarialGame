def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [0, 0]
    best_score = -10**18
    tie = []
    # Prefer: closest resource, and when contested prefer larger distance advantage over opponent.
    # If still tied, prefer moves that reduce distance to board center and avoid stalling.
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best = 10**9
        opp_best = 10**9
        my_dist_adv = -10**9
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if dm < my_best:
                my_best = dm
            if do < opp_best:
                opp_best = do
            adv = do - dm
            if adv > my_dist_adv:
                my_dist_adv = adv

        dist_to_any = my_best
        opp_to_any = opp_best
        center_dist = abs(nx - cx) + abs(ny - cy)
        # Score higher is better
        score = (-dist_to_any) + 0.9 * my_dist_adv + 0.12 * (-opp_to_any) - 0.01 * center_dist
        if score > best_score:
            best_score = score
            best = [dx, dy]
            tie = []
        elif score == best_score:
            # Deterministic tie-break: avoid staying still if possible, then lexicographic preference
            if (dx, dy) != (0, 0) and best == [0, 0]:
                best = [dx, dy]
            elif (dx, dy) != (0, 0) or best != [0, 0]:
                cand = (dx, dy)
                cur = (best[0], best[1])
                if cand > cur:
                    best = [dx, dy]
            else:
                tie.append((dx, dy))
                # no further change

    return best if best in ([d[0], d[1]] for d in dirs) else [0, 0]