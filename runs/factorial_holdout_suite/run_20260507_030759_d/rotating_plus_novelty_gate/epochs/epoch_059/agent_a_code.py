def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)
    if (sx, sy) in res_set:
        return [0, 0]
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Run away from opponent deterministically
            dself = abs(nx - sx) + abs(ny - sy)
            dobj = abs(nx - ox) + abs(ny - oy)
            cand = (dobj, -dself, -dx, -dy)
            if best is None or cand > best:
                best = cand
        return [best[2], best[3]]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources_list = list(res_set)

    best = None
    # Prefer immediate pickup, then race advantage to nearest "contested" resource,
    # then steer toward that resource.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            cand = (10**9, 0, 0, -dx, -dy)
        else:
            best_adv = None
            best_dist = None
            for rx, ry in resources_list:
                ds = manh(nx, ny, rx, ry)
                do = manh(ox, oy, rx, ry)
                adv = (do - ds)  # positive => we arrive earlier
                # tie: prefer closer to us
                key = (adv, -ds, -rx, -ry)
                if best_adv is None or key > best_adv:
                    best_adv = key
                    best_dist = ds
            # small penalty for getting closer to opponent (keeps space vs sweeps)
            opp_prox = manh(nx, ny, ox, oy)
            cand = (best_adv[0] * 1000 + best_adv[1], -best_dist, -opp_prox, -dx, -dy)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]