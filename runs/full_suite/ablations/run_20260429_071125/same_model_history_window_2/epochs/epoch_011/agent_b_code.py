def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None:
            continue
        x, y = p
        obstacles.add((x, y))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    # Evaluate moves by targeting resources where we improve relative to opponent.
    best_key = (10**18, 10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd_self = cheb(nx, ny, sx, sy)  # mostly 0/1, used only for tie-breaking
        best_r = (10**18, 10**18)  # (adv, myd)
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = myd - od  # smaller is better (we are closer than opponent)
            # Prefer immediate pickups and reduce risk of opponent taking sooner.
            if myd == 0:
                adv -= 100
            cand = (adv, myd)
            if cand < best_r:
                best_r = cand
        # Also discourage moves that keep us far from all resources: use second-best proxy via min myd.
        min_myd = 10**18
        for rx, ry in resources:
            mdv = cheb(nx, ny, rx, ry)
            if mdv < min_myd:
                min_myd = mdv
        key = (best_r[0], best_r[1], min_myd, myd_self, dx, dy)
        if key < best_key:
            best_key = key

    return [best_key[4], best_key[5]]