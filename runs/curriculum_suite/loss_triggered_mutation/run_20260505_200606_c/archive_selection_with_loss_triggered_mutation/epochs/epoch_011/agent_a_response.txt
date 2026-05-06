def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cur_r = None
    cur_best = 10**9
    if resources:
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < cur_best:
                cur_best = d
                cur_r = (rx, ry)

    # If no resources: maximize distance from opponent (escape), avoid obstacles.
    if not resources:
        best = (-(10**9), 0)
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or not ok(nx, ny):
                continue
            opp_d = man(nx, ny, ox, oy)
            # Tie-break: prefer staying on-grid center-ish
            center_bias = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)
            cand = (opp_d, center_bias)
            if cand > best:
                best = cand
                best_move = [dx, dy]
        return best_move

    # Counter sweep_rows: focus on states where we are closer to resources than opponent,
    # and where opponent's nearest resource is not strongly favored next.
    best_val = (-10**18, 10**18, 0)  # (score, self_to_own, -opp_dist_tiebreak)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        self_near = 10**9
        opp_near = 10**9
        nearest_res = None
        # compute nearest distances to any resource
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            if d1 < self_near:
                self_near = d1
                nearest_res = (rx, ry)
            d2 = man(ox, oy, rx, ry)
            if d2 < opp_near:
                opp_near = d2
        opp_dist = man(nx, ny, ox, oy)
        # Main: maximize (opp_near - self_near) => we are "winning" the resource race.
        # Secondary: ensure we move toward a resource (smaller self_near).
        # Tertiary: keep some separation to avoid being pinned.
        val = (opp_near - self_near, -self_near, opp_dist)
        cand = (val[0], self_near, -opp_dist)
        if cand > best_val:
            best_val = cand
            best_move = [dx, dy]

    return best_move