def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    def best_target():
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we are closer to; slightly prefer closer overall; break ties deterministically
            key = (do - ds, ds + do * 0.001, rx + ry * 0.01)
            if best is None or key < best[0]:
                best = (key, (rx, ry), ds, do)
        return best[1:] if best else (None, None, None)

    target, ds0, do0 = best_target()
    if target is None:
        # No resources: drift toward center while staying safe and mildly away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestv, bestm = -10**18, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obs_set:
                continue
            v = -dist(nx, ny, cx, cy) + 0.08 * dist(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    rx, ry = target
    # Choose move maximizing next-step advantage: reduced distance to target and increased distance vs opponent
    bestv, bestm = -10**18, (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs_set:
            continue
        ds = dist(nx, ny, rx, ry)
        do = dist(ox, oy, rx, ry)  # opponent position unchanged this turn
        adv = (do - ds)  # higher is better
        # Secondary: keep from letting opponent cut off the target by considering their best alternative
        opp_best_margin = 0
        if resources:
            opp_best_margin = -10**9
            for r2x, r2y in resources:
                if (r2x, r2y) in obs_set:
                    continue
                d2o = dist(ox, oy, r2x, r2y)
                d2s = dist(nx, ny, r2x, r2y)
                m = d2o - d2s
                if m > opp_best_margin:
                    opp_best_margin = m
            # We want our move to reduce opponent's advantage opportunities (so smaller opp_best_margin)
            opp_pen = -0.1 * opp_best_margin
        else:
            opp_pen = 0
        # Tertiary: slight bias to reduce own distance, avoid opponent approach
        v = adv * 10.0 - ds + 0.03 * dist(nx, ny, ox, oy) + opp_pen
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]