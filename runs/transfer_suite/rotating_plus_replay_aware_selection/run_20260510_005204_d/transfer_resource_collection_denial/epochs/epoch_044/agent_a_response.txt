def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource by maximizing how much closer we are than opponent,
    # with secondary preference for more centrally located items.
    best_r = None
    best_key = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        # primary: advantage to us; secondary: avoid giving opponent advantage
        key = (myd - opd, -myd, center, -(rx + ry))
        # smaller (myd-opd) is better, so invert sign by using key order carefully:
        # We'll transform to a comparable tuple where larger is better.
        key2 = ((opd - myd), (-myd), center, (-(rx + ry)))
        if best_key is None or key2 > best_key:
            best_key = key2
            best_r = (rx, ry)
    tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        adv = opd2 - myd2  # positive means we are closer than opponent
        # Extra: prefer moves that reduce distance overall to prevent dithering
        dist_to_target = myd2
        # Extra: if opponent can reach the same target in 0-1, prioritize escape toward a better adjacent resource if visible
        # (still deterministic and local: just small scan of nearby resources).
        local_best = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) <= 2 and (rx, ry) not in obstacles:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                val = od - md
                if val > local_best:
                    local_best = val

        val = (adv, -dist_to_target, local_best, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)))
        if best_val is None or val > best_val:
            best_val = val
            best_mv = [dx, dy]

    return best_mv