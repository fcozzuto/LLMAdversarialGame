def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    if resources:
        for rx, ry in resources:
            if rx == sx and ry == sy:
                return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def opp_choke_to(rx, ry):
        # Count obstacles encountered along a simple chebyshev-aligned path from opponent to resource.
        ax = 0 if ox == rx else (1 if rx > ox else -1)
        ay = 0 if oy == ry else (1 if ry > oy else -1)
        x, y = ox, oy
        steps = cheb(ox, oy, rx, ry)
        c = 0
        for _ in range(steps):
            x += ax
            y += ay
            if (x, y) in blocked:
                c += 1
        return c

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in blocked:
            # Invalid move will be kept in place by engine; skip here to avoid wasting score.
            continue

        myd_now = None
        od_now = None
        move_score = -10**9
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od == 0:
                # Opponent sitting on a resource: deprioritize unless it's also ours now (handled above).
                continue

            choke = opp_choke_to(rx, ry)
            lead = od - myd  # we want positive (we closer)
            if lead >= 0:
                tgt = 3.0 * lead + 2.0 * choke
            else:
                tgt = 1.2