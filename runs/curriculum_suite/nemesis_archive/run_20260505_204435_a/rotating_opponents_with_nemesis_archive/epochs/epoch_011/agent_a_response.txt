def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def center(x, y):
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        dx = x - cx; dy = y - cy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return -(dx + dy)

    if not resources:
        # Retreat while drifting toward center; helps against row-sweeps.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sc = -cheb(nx, ny, ox, oy) + 0.15 * center(nx, ny)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose move that maximizes advantage to the most reachable resource.
    best = None
    cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_adv = None
        best_self_dist = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent to that resource
            # Slightly prefer closer resources and those not in "opponent-dominant" regions.
            dom = do - ds
            sc_local = adv + 0.08 * center(rx, ry) - 0.04 * ds
            if best_adv is None or sc_local > best_adv:
                best_adv = sc_local
                best_self_dist = ds

        # If any resource is genuinely winnable (we are closer), strongly prefer it.
        win_like = any((cheb(nx, ny, rx, ry) < cheb(ox, oy, rx, ry)) for rx, ry in resources)
        # Also add mild "intercept" pressure: don't get too far from the opponent in Chebyshev.
        sc = best_adv + (0.6 if win_like else 0.0) - 0.03 * cheb(nx, ny, ox, oy) + 0.1 * center(nx, ny)

        # Deterministic tie-break: prefer staying closer to center and increasing progress on some resource.
        if best is None or sc > best[0] or (sc == best[0] and (abs(nx - cx) + abs(ny - cy), best_self_dist) < best[2]):
            best = (sc, dx, dy, (abs(nx - cx) + abs(ny - cy), best_self_dist))

    return [best[1], best[2]] if best else [0, 0]