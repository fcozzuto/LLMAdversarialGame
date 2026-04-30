def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Prefer a materially favorable target: self significantly closer than opponent.
        best = None
        best_key = None
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd  # bigger means we are closer
            # Deterministic tie-break: prefer earlier acquisition, then smaller coords.
            key = (margin, -sd, -(rx + 3 * ry), -rx, -ry)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best

        # If we are not really closer, switch to a "sting": pick a resource where opponent is forced far
        # by chebyshev distance plus a corner bias to reduce contest likelihood.
        sd0 = cheb(sx, sy, tx, ty)
        od0 = cheb(ox, oy, tx, ty)
        if od0 - sd0 < 1 and res:
            alt = None
            alt_key = None
            for rx, ry in res:
                sd = cheb(sx, sy, rx, ry)
                od = cheb(ox, oy, rx, ry)
                corner_bias = (rx * (w - 1 - sx) + ry * (h - 1 - sy)) - ((w - 1 - rx) * sx + (h - 1 - ry) * sy)
                # Strongly penalize targets the opponent can reach in roughly the same time.
                key = (-(sd - od), -od, sd, corner_bias, -(rx + 7 * ry))
                if alt is None or key > alt_key:
                    alt = (rx, ry)
                    alt_key = key
            tx, ty = alt

    # Greedy step: maximize improvement toward target, avoid obstacles and prefer reducing opponent contest distance.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        before = cheb(sx, sy, tx, ty)
        after = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Improvement first, then keep ourselves near, and lastly use a deterministic coordinate tie-break.
        improvement = before - after
        # Also discourage moving in ways that increase our distance from the "