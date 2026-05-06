def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a "goal" resource: deny opponent if they're significantly closer; otherwise race.
    # If everything is opponent-closer, switch to interference: move to reduce opponent access.
    scored_res = []
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        scored_res.append((opd - myd, myd, opd, rx, ry))
    scored_res.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    # best_denied: where we are closer (advantage <= 0), prefer strongest denial (most negative opd-myd)
    denied = [t for t in scored_res if t[0] <= -1]  # we are at least 1 step closer
    if denied:
        _, _, _, gx, gy = denied[0]
        mode = 0  # race our denied goal
    else:
        # interference: move to reduce opponent distance to their nearest resource
        _, _, _, gx, gy = min(scored_res, key=lambda t: (t[2], t[1], t[3], t[4]))[3:]
        mode = 1

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = man(nx, ny, gx, gy)
        opd = man(nx, ny, ox, oy)
        g_opd = man(ox, oy, gx, gy)

        # Avoid stepping into positions that are "too adjacent" to opponent when interfering
        adj_pen = 0
        if mode == 1 and man(nx, ny, ox, oy) <= 1:
            adj_pen = -6

        if mode == 0:
            # keep momentum to our goal; also discourage giving opponent a closer route by heading away from them a bit
            val = (-myd, man(ox, oy, gx, gy) - g_opd, -opd, dx, dy)
        else:
            # interference: reduce opponent's distance to their goal and keep near them
            val = (man(ox, oy, gx, gy) - man(ox, oy, gx, gy), myd, -g_opd, -opd, adj_pen, dx, dy)
            # above first component is constant; use remaining for deterministic tie-breaks
            val = (g_opd - man(ox, oy, gx, gy), myd, -g_opd, -opd, adj_pen, dx, dy)

        if best is None or val < best[0]:
            best = (val, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]