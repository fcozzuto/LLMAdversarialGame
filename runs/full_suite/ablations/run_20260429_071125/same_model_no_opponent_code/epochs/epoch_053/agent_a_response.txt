def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def d(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Deterministic target selection: prefer resources where we are closer than opponent.
    res_sorted = sorted(res, key=lambda t: (t[0], t[1]))
    best_t = None
    best_val = None
    for tx, ty in res_sorted:
        myd = d((sx, sy), (tx, ty))
        opd = d((ox, oy), (tx, ty))
        # Smaller is better: my distance minus weighted opponent advantage.
        val = myd - 1.2 * opd
        if best_val is None or val < best_val:
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    myd0 = d((sx, sy), (tx, ty))
    opd0 = d((ox, oy), (tx, ty))

    # Move choice: maximize opponent-lag and reduce distance to chosen target.
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = d((nx, ny), (tx, ty))
        # If landing on/near target is great, also consider moving to reduce opponent lead.
        opd = d((ox, oy), (tx, ty))
        opp_lag = opd - myd
        dist_gain = myd0 - myd
        # Key: prioritize larger opp_lag, then larger dist_gain, then deterministic tie-break.
        key = (opp_lag, dist_gain, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]