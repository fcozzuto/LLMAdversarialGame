def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def step_towards(tx, ty):
        best = (10**9, 10**9, 0, 0, 0)  # (opp_lead, dist, -center_bias, rx, ry)
        cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
        for rx, ry in resources:
            if not inside(rx, ry) and (rx, ry) not in obstacles:
                continue
            myd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            if myd == 0:
                key = (-10**9, 0, 0, rx, ry)
            else:
                center = -((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0))
                # Prefer resources where we can arrive sooner (or tie), heavily.
                # Otherwise penalize where opponent is closer.
                opp_lead = od - myd
                key = (opp_lead, myd, -center, rx, ry)
            if key < best:
                pass
            if best == (10**9, 10**9, 0, 0, 0) or (
                (key[0], key[1], key[2]) < (best[0], best[1], best[2])
            ):
                best = key
                tx, ty = rx, ry
        return tx, ty

    if not resources:
        return [0, 0]

    # Choose a resource that we can secure; if none, choose the least contested.
    tx, ty = resources[0]
    tx, ty = step_towards(tx, ty)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    # Evaluate moves: secure immediate pickups; otherwise maximize our lead on target
    # and avoid stepping away from target when contested.
    best_m = [0, 0]
    best_val = None
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    resset = set((p[0], p[1]) for p in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        picked = 1 if (nx, ny) in resset else 0

        myd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Opponent shadow tends to mirror; we bias slightly toward center to reduce their
        # ability to cut across while still aiming for the target.
        center_bias = -((nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0))
        opp_lead = od - myd  # positive means opponent closer
        # High reward for pick-up, then prefer making opp_lead non-positive (we are not behind),
        # then minimize our remaining distance.
        val = (-(picked * 1000), opp_lead, myd, -center_bias, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]