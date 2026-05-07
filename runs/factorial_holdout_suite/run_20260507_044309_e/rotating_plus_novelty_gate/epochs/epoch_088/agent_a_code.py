def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res = [tuple(r) for r in resources]
    res_set = set(res)

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # Choose move that maximizes "lead" on best target resource
    best_move = [0, 0]
    best_score = -10**18
    opp_damp = 1  # deterministic, small bias

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best resource after this move: prefer resources we approach faster than opponent
        local_best = -10**18
        for rx, ry in res:
            ds_before = cheb(sx, sy, rx, ry)
            ds_after = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Gain: reduce distance our-side; also prefer resources we can reach earlier
            # Tie-breakers: slightly prefer staying toward center-ish (avoid dithering near borders).
            reach_adv = (do - ds_after) - opp_damp * (ds_after - ds_before)
            center_pref = -abs(nx - (w - 1) / 2) * 0.01 - abs(ny - (h - 1) / 2) * 0.01
            val = reach_adv * 10 + (-ds_after) + center_pref
            if val > local_best:
                local_best = val

        # If no resources, just keep away from obstacles and drift toward opponent's likely direction (toward them by cheb)
        if not res:
            local_best = -cheb(nx, ny, ox, oy) * 5 + (-abs(nx - (w - 1))) * 0.01

        if local_best > best_score:
            best_score = local_best
            best_move = [dx, dy]

    return best_move