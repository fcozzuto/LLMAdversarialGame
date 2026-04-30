def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_resource_dist(x, y):
        if not resources:
            return 10**9
        d = 10**9
        for rx, ry in resources:
            dd = cheb(x, y, rx, ry)
            if dd < d:
                d = dd
        return d

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    my_here_has_resource = (sx, sy) in obst  # never true; keep deterministic
    if resources and (sx, sy) in {(r[0], r[1]) for r in resources}:
        return [0, 0]

    # Precompute to avoid repeated loops
    res_set = {(r[0], r[1]) for r in resources}
    opp_dist_now = cheb(sx, sy, ox, oy)

    best = None
    for dx, dy, nx, ny in legal:
        # Primary: grab if on a resource now
        grab = 1 if (nx, ny) in res_set else 0
        # Move closer to nearest resource (tie-break by opp distance)
        my_to_res = nearest_resource_dist(nx, ny)
        opp_dist_after = cheb(nx, ny, ox, oy)

        # Small shaping: prefer increasing distance from opponent; penalize moving too close
        opp_gain = opp_dist_after - opp_dist_now

        # Deterministic ordering with tuple key
        key = (-grab, my_to_res, -(opp_gain), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]