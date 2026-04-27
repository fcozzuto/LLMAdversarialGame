def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # No resources: move toward center while keeping away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            dcent = abs(nx - cx) + abs(ny - cy)
            dsep = abs(nx - ox) + abs(ny - oy)
            sc = -dcent + 0.02 * dsep
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick resource we are most advantaged to reach sooner
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        adv = (do - ds)  # positive means we're closer
        # slight tie-break toward nearer resource overall
        adv2 = adv * 10 - ds
        if adv2 > best_adv:
            best_adv = adv2
            best_res = (rx, ry)

    rx, ry = best_res
    best = (0, 0)
    best_sc = -10**18

    # Evaluate possible next moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = manh(nx, ny, rx, ry)
        do_now = manh(ox, oy, rx, ry)
        dsep_next = manh(nx, ny, ox, oy)

        # Prefer reaching resource, and discourage opponent intercept by staying farther from them
        sc = -ds_next * 5 + (do_now - ds_next) * 2 + dsep_next * 0.05

        # Mild preference to reduce distance to opponent when we're equally good (avoid getting stuck)
        if do_now == ds_next:
            sc += 0.5 * dsep_next

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]