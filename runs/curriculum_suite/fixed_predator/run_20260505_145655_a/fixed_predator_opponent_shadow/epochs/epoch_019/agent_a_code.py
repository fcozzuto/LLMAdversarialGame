def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        # Keep pressure: move toward opponent
        return [-sign(ox - x), -sign(oy - y)]

    # Precompute opponent nearest distance to each resource
    res_list = [tuple(r) for r in resources]
    opp_dists = []
    for rx, ry in res_list:
        opp_dists.append(dist(rx, ry, ox, oy))

    best_mv = (0, 0)
    best_sc = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        self_near = 999
        opp_near = 999
        # Prefer moves that create a close lead on some resource, and secondarily reduce our nearest distance
        lead_sum = 0
        winish = 0
        for i, (rx, ry) in enumerate(res_list):
            sd = dist(nx, ny, rx, ry)
            od = opp_dists[i]
            self_near = sd if sd < self_near else self_near
            opp_near = od if od < opp_near else opp_near
            adv = od - sd  # positive => we are closer than opponent
            if adv > 0:
                winish += 1
                lead_sum += adv * 20 - sd  # favor bigger leads and nearer targets

        # Denial term: moves that also push opponent away from resources slightly
        # (approx by increasing distance for opponent to its nearest resource)
        denom = 0
        for i, (rx, ry) in enumerate(res_list):
            od = opp_dists[i]
            denom = od if od < denom else denom
        # simple opponent denial: our move toward opponent generally increases their contest difficulty
        opp_push = -dist(nx, ny, ox, oy)

        # Combine with tie-breakers deterministically
        sc = lead_sum + winish * 200 - self_near * 3 + opp_push * 0.1 + (opp_near - 999) * 0.01

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)
        elif sc == best_sc:
            # deterministic tie-break: prefer smaller distance to nearest resource, then smaller dx,dy lexicographically
            cand_dn = None
            best_dn = None
            # compute nearest for tie-break
            for rx, ry in res_list:
                sd = dist(nx, ny, rx, ry)
                cand_dn = sd if cand_dn is None or sd < cand_dn else cand_dn
            bx, by = x + best_mv[0], y + best_mv[1]
            for rx, ry in res_list:
                sd = dist(bx, by, rx, ry)
                best_dn = sd if best_dn is None or sd < best_dn else best_dn
            if cand_dn is not None and best_dn is not None:
                if cand_dn < best_dn:
                    best_mv = (dx, dy)
                elif cand_dn == best_dn:
                    if (dx, dy) < best_mv:
                        best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]