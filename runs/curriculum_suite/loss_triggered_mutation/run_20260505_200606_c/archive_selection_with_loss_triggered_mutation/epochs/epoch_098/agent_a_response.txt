def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best = None
    # Prefer moves that secure a resource (max advantage), then keep closeness and reduce opponent proximity.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate by the best resource we could aim for from (nx, ny).
        best_adv = -10**9
        best_my = 10**9
        best_opp = 10**9
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            adv = oppd - myd  # positive means we are closer than opponent
            if adv > best_adv or (adv == best_adv and myd < best_my):
                best_adv = adv
                best_my = myd
                best_opp = oppd
        # Additional pressure: avoid giving opponent an easier direct path to our current chosen target vicinity.
        # Also gently prefer progressing away from being trapped by obstacles via center bias.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = - (abs(nx - cx) + abs(ny - cy)) * 0.001
        # Opponent interference: move to increase their distance to our nearest target resource.
        opp_nearest_to_us = min(man(nx, ny, rx, ry) for rx, ry in res)
        my_nearest = opp_nearest_to_us
        # Deterministic composite key: maximize best_adv, then minimize best_my, then minimize best_opp, then prefer dx/dy order.
        key = (-(best_adv), best_my, best_opp, abs(dx) + abs(dy), center_bias, my_nearest)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]