def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def best_resource_score(nx, ny):
        if not resources:
            return 0, 0
        bd = 10**9
        for rx, ry in resources:
            d = dist(nx, ny, rx, ry)
            if d < bd:
                bd = d
        # prefer closer to resources and slightly toward center
        return bd, abs(nx - cx) + abs(ny - cy)

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_my_o = dist(nx, ny, ox, oy)
        d_center = abs(nx - cx) + abs(ny - cy)
        rdist, rcenter = best_resource_score(nx, ny)
        # If opponent is closer to the target, run away; otherwise advance.
        # Also keep away from obstacles by favoring squares with more open neighbors.
        open_n = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                open_n += 1
        if resources:
            opp_to_res = 10**9
            for rx, ry in resources:
                dd = dist(ox, oy, rx, ry)
                if dd < opp_to_res:
                    opp_to_res = dd
            ahead = (rdist <= opp_to_res)
            run_factor = -1 if ahead else 1  # ahead: minimize opponent distance, else maximize
        else:
            run_factor = 1
        key = (
            run_factor * d_my_o,
            rdist,
            -open_n,
            d_center + 0.001 * rcenter,
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]